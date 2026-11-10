# Control 2.13 — Verification & Testing: Documentation and Record Keeping

**Control:** 2.13 — Documentation and Record Keeping
**Pillar:** Pillar 2 — Management
**Audience:** SharePoint Admin, Purview Records Manager, Purview Compliance Admin, Compliance Officer, AI Governance Lead, Internal Audit
**Companion playbooks:** [Portal Walkthrough](./portal-walkthrough.md) · [PowerShell Setup](./powershell-setup.md) · [Troubleshooting](./troubleshooting.md)
**Last UI verified:** April 2026
**Last Verified:** 2026-11-09 (affected product assertions checked against live documentation; tenant tests not executed)

---

## Regulatory hedging notice

This verification playbook is intended to help support FSI organizations in confirming that documentation and record-keeping controls are configured and operating as expected. It aids in meeting expectations from FINRA Rule 4511, FINRA Rule 3110, SEC Rules 17a-3/4, SOX §§302/404, GLBA 501(b), OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12), Federal Reserve SR 26-2 (formerly SR 11-7), and CFTC Regulation 1.31.

A clean run of this playbook **does not guarantee legal or regulatory compliance**, does not by itself constitute a 17a-4(f) attestation, and does not replace the firm's written supervisory procedures or independent records-management assessment. Organizations should verify configuration meets their specific regulatory obligations.

---

## Pre-Gate Checks

Before executing test cases, confirm the following pre-gates are met:

| Pre-Gate | Requirement | Verification Method |
|---|---|---|
| PRE-01 | SharePoint Admin role assigned to test operator | Entra ID role assignments |
| PRE-02 | Purview Records Manager has the Purview **Records Management** role group | Purview portal role groups; this is not an Entra directory role of the same name |
| PRE-03 | AI Governance SharePoint site provisioned | Navigate to site URL |
| PRE-04 | Retention labels created and published | Purview portal > **Solutions** > **Records Management** > **File plan** and **Policies** > **Label policies** |
| PRE-05 | Zone classification documented for agents under test | Control 2.2 zone register |
| PRE-06 | Evidence directory created at `C:\fsi-evidence\2.13` | PowerShell: `Test-Path C:\fsi-evidence\2.13` |

---

## Test Cases

### TC-2.13-001 — SharePoint Site Structure Exists

| Field | Detail |
|---|---|
| **Objective** | Verify the AI Governance SharePoint site and all required document libraries exist |
| **Zone Applicability** | Zone 1, Zone 2, Zone 3 |
| **Preconditions** | PRE-01, PRE-03 |
| **Steps** | 1. Navigate to the AI Governance SharePoint site URL<br>2. Verify site loads and the user has access<br>3. Navigate to **Site contents**<br>4. Verify the following libraries exist: `AgentConfigurations`, `InteractionLogs`, `GovernanceDecisions` (Zone 1 minimum)<br>5. For Zone 2+: verify `ApprovalRecords`, `IncidentReports`, `SupervisionRecords` also exist |
| **Expected Result** | All zone-required libraries are present with correct names |
| **Pass Criteria** | All required libraries listed in Site contents |
| **Fail Criteria** | Any required library is missing or inaccessible |
| **Evidence to Capture** | Screenshot of Site contents page showing all libraries; export via PowerShell: `Get-PnPList | Where-Object { $_.BaseTemplate -eq 101 } | Select-Object Title, ItemCount | Export-Csv` |

---

### TC-2.13-002 — Metadata Schema Applied to Libraries

| Field | Detail |
|---|---|
| **Objective** | Verify AI Governance metadata columns are present on all document libraries |
| **Zone Applicability** | Zone 1 (3 core columns), Zone 2+ (7 columns) |
| **Preconditions** | PRE-01, TC-2.13-001 passed |
| **Steps** | 1. Navigate to each library > **Settings** > **Library settings** > **Columns**<br>2. Verify the following columns appear: `Agent ID`, `Document Category`, `Classification Date`<br>3. For Zone 2+: verify `Regulatory Reference`, `Retention Period`, `Governance Zone`, `Record Owner` also appear; compare internal names with the automation schema<br>4. Upload a test document and confirm all required metadata fields are available for population before applying record labels |
| **Expected Result** | All zone-required metadata columns are present in each library |
| **Pass Criteria** | All columns visible and editable when uploading/editing documents |
| **Fail Criteria** | Any required column is missing from any governed library |
| **Evidence to Capture** | Screenshot of column list for each library; PowerShell: `Get-PnPField | Where-Object { $_.Group -eq 'AI Governance' } | Select-Object InternalName, Title, TypeDisplayName | Export-Csv` |

---

### TC-2.13-003 — Retention Labels Created with Correct Periods

| Field | Detail |
|---|---|
| **Objective** | Verify Purview retention labels exist with correct retention periods per the SEC 17a-4 record-type matrix |
| **Zone Applicability** | Zone 2 (standard labels), Zone 3 (+ regulatory record labels) |
| **Preconditions** | PRE-02, PRE-04 |
| **Steps** | 1. Open **Purview portal** > **Solutions** > **Records Management** > **File plan**<br>2. Search for labels beginning with `FSI-Agent`<br>3. For each label, verify:<br>   - Name matches expected naming convention<br>   - Retention duration, units, and start trigger match the approved schedule; do not treat fixed day counts as calendar-year arithmetic<br>   - Content is retained during the period and disposition matches the approved action (retain-then-delete in this portal example; deletion-only does not preserve content)<br>   - Record type is correct (Item, Record, or Regulatory record), including default lock state<br>4. With disposable standard-record test data, verify locked content cannot be edited or deleted; verify authorized unlocking permits edits under record versioning. Do not expect standard records to have regulatory-record label-removal restrictions<br>5. For regulatory records, verify content/properties and label removal are blocked, and application is from a published label policy, not auto-apply |
| **Expected Result** | Zone 2: at least 5 labels (Communications-3Year, BooksRecords-6Year, Governance-6Year, Supervision-6Year, Configuration-6Year). Zone 3: add RegRecord-7Year, CFTC-5Year, ModelRisk-6Year; verify Permanent if created through the portal |
| **Pass Criteria** | All expected labels present with correct retention periods and record types |
| **Fail Criteria** | Any expected label missing, or retention period does not match specification |
| **Evidence to Capture** | Screenshot of Purview Labels page showing all FSI-Agent labels; PowerShell: `Get-ComplianceTag | Where-Object { $_.Name -like 'FSI-Agent*' } | Select-Object Name, RetentionDuration, RetentionAction, IsRecordLabel | Export-Csv` |

---

### TC-2.13-004 — Retention Policy Published and Active

| Field | Detail |
|---|---|
| **Objective** | Verify retention label policies are published to the AI Governance SharePoint site and are in active (enabled) state |
| **Zone Applicability** | Zone 2, Zone 3 |
| **Preconditions** | PRE-02, TC-2.13-003 passed |
| **Steps** | 1. Open **Purview portal** > **Solutions** > **Records Management** > **Policies** > **Label policies**<br>2. Locate the FSI-AI-Governance-Retention policies of type **Publish** and check distribution status; simulation applies to auto-apply policies, not publication<br>3. For the group-connected governance team site and a static scope, verify the group is selected under **Microsoft 365 Group mailboxes & sites**; for a non-group-connected site verify **SharePoint classic and communication sites**<br>4. Verify the published labels are actually available on a test document in the target library, allowing up to 7 days<br>5. For Zone 3: verify its additional labels are published; the PowerShell sample creates one policy per label |
| **Expected Result** | At least one active retention policy targets the AI Governance site with all required labels |
| **Pass Criteria** | Publication distributed without errors, correct group/site scoped, and required labels available in the target library |
| **Fail Criteria** | Policy missing, disabled, or not targeting the correct SharePoint site |
| **Evidence to Capture** | Screenshot of policy type, distribution status, labels, and group/site location; PowerShell: `Get-RetentionCompliancePolicy | Where-Object { $_.Name -like '*FSI*' } | Select-Object Name, Mode, Enabled, SharePointLocation, ModernGroupLocation | Export-Csv` |

---

### TC-2.13-005 — Auto-Labeling Policy Operational

| Field | Detail |
|---|---|
| **Objective** | Verify auto-labeling policies are configured and applying retention labels to agent interaction logs |
| **Zone Applicability** | Zone 2 (recommended), Zone 3 (required) |
| **Preconditions** | PRE-02, TC-2.13-004 passed, allow 7+ days after label publishing |
| **Steps** | 1. Review the auto-apply policy query, group/site scope, simulation results, and deployed status. Confirm `ParentLink` targets the actual `InteractionLogs` URL<br>2. Upload an unlabeled test document there with "Agent ID: TEST-001" and "Copilot interaction" in the content; add a negative sample outside the library and one without the matching text<br>3. Allow indexing and up to **7 days** for automatic application after deployment<br>4. Verify `FSI-Agent-Communications-3Year` (or the configured standard-record auto-label) is applied only to matching samples. An existing retention label must not be replaced; regulatory-record labels are not supported by auto-apply policies |
| **Expected Result** | The uploaded document has the correct retention label automatically applied |
| **Pass Criteria** | Auto-applied label matches the expected label per the auto-labeling policy |
| **Fail Criteria** | No label applied after 7 days with confirmed indexing and policy deployment, wrong label applied, or negative samples labeled by this policy |
| **Evidence to Capture** | Screenshot of document properties showing the auto-applied retention label with timestamp; document properties export |

---

### TC-2.13-006 — SEC 17a-4 Compliant Storage Configured (Zone 3 Only)

| Field | Detail |
|---|---|
| **Objective** | Verify WORM storage or audit-trail alternative is configured for Zone 3 agent records |
| **Zone Applicability** | Zone 3 only |
| **Preconditions** | PRE-02, Zone 3 deployment confirmed |
| **Steps** | **Option A (WORM):**<br>1. Open **Azure Portal** > **Storage accounts** > locate the FSI governance storage account<br>2. Navigate to **Data storage** > **Containers** > `ai-governance-records` > **More** > **Access policy**<br>3. Verify **Immutable blob storage** is configured with a container-scoped time-based retention policy; do not require blob versioning for this scope<br>4. Verify the policy is **Locked** (not unlocked)<br>5. Verify retention period ≥ 2190 days (6 years)<br>6. After allowing up to 35 seconds for activation, attempt deletion and overwrite of disposable test blobs still under retention — verify both are blocked; never use production records<br><br>**Option B (Audit-trail):**<br>1. Review the audit-trail alternative documentation in WSPs<br>2. Verify DEO representation or DTP undertaking is on file<br>3. Verify Cohasset (or equivalent) attestation is current<br>4. Verify serialized indexing is operational |
| **Expected Result** | WORM: locked policy with ≥ 6-year retention, deletion blocked. Audit-trail: documentation complete and current |
| **Pass Criteria** | Either Option A or Option B fully verified with all sub-checks passing |
| **Fail Criteria** | WORM policy unlocked, retention period insufficient, or audit-trail documentation incomplete |
| **Evidence to Capture** | Option A: Screenshot of container access policy showing locked time-based retention; deletion attempt error message. Option B: Copy of DEO/DTP undertaking and attestation document |

---

### TC-2.13-007 — Document Version History Preserved

| Field | Detail |
|---|---|
| **Objective** | Verify SharePoint versioning is enabled and preserving document history for governance records |
| **Zone Applicability** | Zone 1, Zone 2, Zone 3 |
| **Preconditions** | TC-2.13-001 passed |
| **Steps** | 1. Navigate to each governed library > **Settings** > **Library settings** > **Versioning settings**<br>2. Verify **Create major versions** is selected<br>3. Verify the major-version count limit is ≥ 500 (not the draft limit) and capture version expiration settings separately<br>4. Upload an unlabeled test document, edit it, save — verify version 2.0 is created<br>5. Click **Version history** on the document and verify both versions are listed |
| **Expected Result** | Versioning enabled, edits create new versions, version history is viewable |
| **Pass Criteria** | Versioning on, version limit ≥ 500, test document shows version history |
| **Fail Criteria** | Versioning disabled, version limit too low, or version history not maintained |
| **Evidence to Capture** | Screenshot of versioning settings for each library; screenshot of test document version history |

---

### TC-2.13-008 — Copilot Studio Agent Version History Documented

| Field | Detail |
|---|---|
| **Objective** | Verify Microsoft Copilot Studio publication release records, solution version/history, and source export are preserved |
| **Zone Applicability** | Zone 2, Zone 3 |
| **Preconditions** | Access to agent and Dataverse solution; at least System Customizer for export. Managed Environment status is not a prerequisite for viewing solution history |
| **Steps** | 1. Open the agent in **Copilot Studio** in the correct environment > **Publish**; capture the displayed status<br>2. Verify a release record binds agent/environment IDs, operator identity, publication timestamp, approval, and solution version<br>3. Open **Settings** > **Agent details** > **View solution**; in Power Apps > same environment > **Solutions** > select solution > **See history**, capture operation, version, timestamps, and result. Preserve before the 180-day cleanup; the solution **Publisher** is not the human release operator<br>4. For layers: solution > **Agents** > agent > **Advanced** > **See solution layers**<br>5. Verify the custom unmanaged source solution export, required-object inventory, and documented exclusions are in `AgentConfigurations`. For managed targets, use the preserved source deployment ZIP, not a target export<br>6. Confirm Dataverse auditing at environment, required-table, and column levels under PPAC > **Manage** > **Environments** > environment > **Settings** > **Audit and logs** > **Audit settings** and the table/column settings |
| **Expected Result** | Release record, publication evidence, solution history/layers, and dependency-checked source export preserved |
| **Pass Criteria** | Latest deployed agent matches its release record and source package; evidence is captured before history cleanup; auditing scope documented |
| **Fail Criteria** | Missing release record/source package, mismatched solution version, or solution operation history incorrectly presented as publication history |
| **Evidence to Capture** | Agent details and Publish screenshots; release record; solution history and layers; source ZIP and dependency/exclusion inventory; audit settings. Do not substitute `Get-AdminPowerApp` output for agent definitions |

---

### TC-2.13-009 — Examination Response Procedure Documented

| Field | Detail |
|---|---|
| **Objective** | Verify the examination response procedure exists and includes all required elements |
| **Zone Applicability** | Zone 2 (basic), Zone 3 (comprehensive with legal hold integration) |
| **Preconditions** | TC-2.13-001 passed |
| **Steps** | 1. Navigate to `GovernanceDecisions` library<br>2. Locate `Examination-Response-Procedure` document<br>3. Open and verify it includes:<br>   - Designated custodian names and contact information<br>   - Backup custodian designation<br>   - Response SLA (expected: 24hr acknowledgment, 48hr initial production)<br>   - Search procedures for agent records<br>   - Export and production procedures<br>   - Chain of custody documentation process<br>4. For Zone 3: verify legal hold integration section referencing Control 1.19 |
| **Expected Result** | Procedure document exists with all required sections populated |
| **Pass Criteria** | Document exists, all sections present, custodians named, SLAs defined |
| **Fail Criteria** | Document missing, incomplete sections, no custodians designated |
| **Evidence to Capture** | Copy of the examination response procedure document; document properties showing retention label and metadata |

---

### TC-2.13-010 — Documentation Completeness Audit Executed

| Field | Detail |
|---|---|
| **Objective** | Verify that documentation completeness audits are being conducted at the required cadence |
| **Zone Applicability** | Zone 1 (annual), Zone 2 (quarterly), Zone 3 (monthly) |
| **Preconditions** | TC-2.13-001 passed |
| **Steps** | 1. Navigate to `GovernanceDecisions` library<br>2. Locate audit schedule document and most recent audit report<br>3. Verify audit was conducted within the required cadence:<br>   - Zone 1: within the last 12 months<br>   - Zone 2: within the last 90 days<br>   - Zone 3: within the last 30 days<br>4. Verify the audit report covers: library completeness, label application, metadata population, version history, access controls<br>5. Verify any audit findings have documented remediation plans |
| **Expected Result** | Current audit report exists within the required cadence window |
| **Pass Criteria** | Audit report is current, covers all required areas, findings have remediation plans |
| **Fail Criteria** | No audit report, report outside cadence window, findings without remediation |
| **Evidence to Capture** | Copy of most recent audit report; audit schedule showing compliance with cadence |

---

### TC-2.13-011 — Record Access Controls Validated

| Field | Detail |
|---|---|
| **Objective** | Verify that governance document library permissions restrict access to authorized personnel only |
| **Zone Applicability** | Zone 2, Zone 3 |
| **Preconditions** | TC-2.13-001 passed, SharePoint Admin role |
| **Steps** | 1. Navigate to each governed library > **Settings** > **Permissions for this document library**<br>2. Verify the library has unique permissions (not inheriting from site)<br>3. Verify access is limited to:<br>   - SharePoint Admin (Full Control)<br>   - Purview Records Manager (Contribute)<br>   - Compliance Officer (Read or Contribute)<br>   - AI Governance Lead (Contribute)<br>4. Verify no "Everyone" or "All Users" permissions exist<br>5. For Zone 3: verify external sharing is disabled on all governed libraries |
| **Expected Result** | Library permissions are restricted to named governance roles; no overly permissive access |
| **Pass Criteria** | Unique permissions applied, only authorized roles have access, no broad sharing |
| **Fail Criteria** | Inherited permissions, Everyone/All Users in permissions, external sharing enabled |
| **Evidence to Capture** | Screenshot of permissions page for each library; PowerShell: `Get-PnPGroup | Select-Object Title, Users | Export-Csv` |

---

### TC-2.13-012 — OCC Bulletin 2026-13 / Fed SR 26-2 Model Documentation (Zone 3)

| Field | Detail |
|---|---|
| **Objective** | Verify that agents classified as models have model risk documentation per OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7) |
| **Zone Applicability** | Zone 3 (agents classified as models) |
| **Preconditions** | Agent classified as a model per OCC Bulletin 2026-13 (formerly OCC 2011-12) definition |
| **Steps** | 1. Review the model inventory (per [Control 3.1](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md)) for agents classified as models<br>2. For each model-classified agent, verify the following documentation exists in the governance library:<br>   - Model development documentation (purpose, methodology, assumptions)<br>   - Validation evidence (initial validation and most recent periodic review)<br>   - Ongoing monitoring reports (performance metrics, drift analysis)<br>   - Change documentation (configuration changes with approvals)<br>3. Verify the `FSI-Agent-ModelRisk-6Year` retention label is applied to all model documentation<br>4. Verify a named Model Risk Manager is assigned |
| **Expected Result** | Complete model risk documentation exists for each model-classified agent |
| **Pass Criteria** | All four documentation categories present, correct retention label applied, owner assigned |
| **Fail Criteria** | Any documentation category missing, wrong retention label, no owner |
| **Evidence to Capture** | List of model-classified agents with documentation status; screenshot of model documentation folder with retention labels visible |

---

## Test Execution Summary Template

| Test Case | Zone | Status | Tester | Date | Notes |
|---|---|---|---|---|---|
| TC-2.13-001 | All | ☐ Pass ☐ Fail | | | |
| TC-2.13-002 | All | ☐ Pass ☐ Fail | | | |
| TC-2.13-003 | 2+ | ☐ Pass ☐ Fail | | | |
| TC-2.13-004 | 2+ | ☐ Pass ☐ Fail | | | |
| TC-2.13-005 | 2+ | ☐ Pass ☐ Fail | | | |
| TC-2.13-006 | 3 | ☐ Pass ☐ Fail ☐ N/A | | | |
| TC-2.13-007 | All | ☐ Pass ☐ Fail | | | |
| TC-2.13-008 | 2+ | ☐ Pass ☐ Fail | | | |
| TC-2.13-009 | 2+ | ☐ Pass ☐ Fail | | | |
| TC-2.13-010 | All | ☐ Pass ☐ Fail | | | |
| TC-2.13-011 | 2+ | ☐ Pass ☐ Fail | | | |
| TC-2.13-012 | 3 | ☐ Pass ☐ Fail ☐ N/A | | | |

---

## Auditor Evidence Pack

The following artifacts constitute the evidence pack for Control 2.13. Maintain all artifacts in the `C:\fsi-evidence\2.13` directory with SHA-256 hashes recorded in the evidence manifest.

| # | Artifact | Source | Location | SHA-256 Manifest Reference |
|---|---|---|---|---|
| 1 | SharePoint library inventory CSV | §2.3 of PowerShell Setup | `library-inventory-{stamp}.csv` | `manifest-2.13-{stamp}.csv` row 1 |
| 2 | Site columns configuration CSV | §3.2 of PowerShell Setup | `site-columns-{stamp}.csv` | `manifest-2.13-{stamp}.csv` row 2 |
| 3 | Retention labels inventory CSV | §7 of PowerShell Setup | `retention-labels-{stamp}.csv` | `manifest-2.13-{stamp}.csv` row 3 |
| 4 | Retention policies inventory CSV | §7 of PowerShell Setup | `retention-policies-{stamp}.csv` | `manifest-2.13-{stamp}.csv` row 4 |
| 5 | Documentation completeness audit CSV | §6 of PowerShell Setup | `doc-completeness-audit-{stamp}.csv` | `manifest-2.13-{stamp}.csv` row 5 |
| 6 | Source agent solution ZIP and publication release record | §8 of PowerShell Setup; Portal Steps 10 and 16 | Saved solution ZIP, release CSV, and dependency/exclusion inventory | Separate manifest entries per saved file |
| 7 | Validation results CSV | §10 of PowerShell Setup | `validation-results-{stamp}.csv` | `manifest-2.13-{stamp}.csv` row 7 |
| 8 | Retention label creation evidence (JSON per label) | §4 of PowerShell Setup | `label-{name}-{stamp}.json` | Separate entries per label |
| 9 | Retention policy creation evidence (JSON per policy) | §5 of PowerShell Setup | `policy-{name}-{stamp}.json` | Separate entries per policy |
| 10 | PowerShell transcript | §1.3 of PowerShell Setup | `transcript-2.13-{stamp}.log` | Final transcript hash |
| 11 | Evidence manifest (master) | §9 of PowerShell Setup | `manifest-2.13-{stamp}.csv` | Self-referencing (manifest hash printed to console) |
| 12 | Site creation screenshot | Portal Walkthrough Step 1 | `evidence-2.13-site-creation.png` | Manual entry |
| 13 | Agent Publish-page and solution history/layer screenshots | Portal Walkthrough Steps 10 and 16 | Screenshots paired with the release record and source ZIP | Manual entry |
| 14 | WORM policy screenshot (Zone 3) | TC-2.13-006 | `evidence-2.13-worm-policy.png` | Manual entry |
| 15 | Examination response procedure | Portal Walkthrough Step 14 | `Examination-Response-Procedure.docx` | Manual entry |

### Manifest integrity verification

To verify the evidence pack integrity at any point:

```powershell
$manifest = Import-Csv 'C:\fsi-evidence\2.13\manifest-2.13-{stamp}.csv'
$failures = @()
foreach ($entry in $manifest) {
    if (Test-Path $entry.FullPath) {
        $currentHash = (Get-FileHash -Path $entry.FullPath -Algorithm SHA256).Hash
        if ($currentHash -ne $entry.SHA256) {
            Write-Host "[TAMPERED] $($entry.File) — expected $($entry.SHA256), got $currentHash" -ForegroundColor Red
            $failures += $entry.File
        } else {
            Write-Host "[INTACT] $($entry.File)" -ForegroundColor Green
        }
    } else {
        Write-Host "[MISSING] $($entry.File)" -ForegroundColor Red
        $failures += $entry.File
    }
}
if ($failures.Count -eq 0) {
    Write-Host "`n[PASS] All evidence artifacts verified — integrity intact" -ForegroundColor Green
} else {
    Write-Host "`n[FAIL] $($failures.Count) artifact(s) failed integrity check" -ForegroundColor Red
}
```

---

## Attestation Statement Template

```markdown
## Control 2.13 Attestation — Documentation and Record Keeping

**Organization:** [Organization Name]
**Control Owner:** [Name / Role]
**Attestation Date:** [Date]
**Governance Zone:** [Zone 1 / Zone 2 / Zone 3]

I attest that the following documentation and record-keeping controls have been
verified and are operating as designed:

1. **SharePoint site hierarchy** is established for AI governance:
   - Site URL: [URL]
   - Libraries configured: [Count and list]
   - Metadata schema: [Column count] columns in AI Governance group

2. **Purview retention labels** are configured and published:
   - Labels created: [Count]
   - Retention periods verified per SEC 17a-4 record-type matrix
   - Publication distributed; target group/site and published label inventory: [Details]

3. **Auto-labeling** (Zone 2+):
   - Auto-labeling policy: [Enabled / Not applicable]
   - Policy targets: [Group/site and actual library ParentLink query]
   - Simulation/deployment status and matching/negative sample results: [Evidence]
   - Existing labels preserved; no regulatory-record auto-apply policy: [Verified]

4. **SEC 17a-4 compliant storage** (Zone 3):
   - Method: [WORM / Audit-trail alternative / Not applicable]
   - Policy locked: [Yes / No / N/A]
   - Retention period: [Days]

5. **Examination response procedures** are documented:
   - Custodian: [Name]
   - Backup custodian: [Name]
   - Response SLA: [Hours]

6. **Documentation completeness audit:**
   - Last audit date: [Date]
   - Cadence: [Annual / Quarterly / Monthly]
   - Findings remediated: [Yes / In progress / N/A]

**Evidence manifest:** manifest-2.13-[stamp].csv
**Manifest SHA-256:** [hash]

**Attester Signature:** _______________________
**Compliance Officer Review:** _______________________
**Date:** _______________________
```

!!! note "Attestation does not constitute legal certification"
    This attestation template supports internal governance record-keeping and aids in demonstrating control operating effectiveness. It does not constitute a legal certification of regulatory compliance. Organizations should verify attestation requirements with their compliance and legal teams.

---

[Back to Control 2.13](../../../controls/pillar-2-management/2.13-documentation-and-record-keeping.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: November 2026 | Version: v1.6.2 | UI Verification Status: Needs Review (documentation verified 2026-11-09; tenant tests pending)*
