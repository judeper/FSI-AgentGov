# Control 2.13 — Verification & Testing: Documentation and Record Keeping

**Control:** 2.13 — Documentation and Record Keeping
**Pillar:** Pillar 2 — Management
**Audience:** SharePoint Admin, Purview Records Manager, Purview Compliance Admin, Compliance Officer, AI Governance Lead, Internal Audit
**Companion playbooks:** [Portal Walkthrough](./portal-walkthrough.md) · [PowerShell Setup](./powershell-setup.md) · [Troubleshooting](./troubleshooting.md)
**Last UI verified:** April 2026

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
| PRE-02 | Purview Records Manager role assigned | Entra ID role assignments |
| PRE-03 | AI Governance SharePoint site provisioned | Navigate to site URL |
| PRE-04 | Retention labels created and published | Purview portal > Data lifecycle management > Labels |
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
| **Steps** | 1. Navigate to each library > **+ Add column** dropdown<br>2. Verify the following columns appear: `Agent ID`, `Document Category`, `Classification Date`<br>3. For Zone 2+: verify `Regulatory Reference`, `Retention Period`, `Governance Zone`, `Record Owner` also appear<br>4. Upload a test document and confirm all required metadata fields are available for population |
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
| **Steps** | 1. Open **Purview portal** > **Data lifecycle management** > **Microsoft 365** > **Labels**<br>2. Search for labels beginning with `FSI-Agent`<br>3. For each label, verify:<br>   - Name matches expected naming convention<br>   - Retention period matches specification (1095 days = 3yr, 2190 = 6yr, 2555 = 7yr, 1825 = 5yr)<br>   - Retention action is correct (KeepAndDelete or Delete)<br>   - Record type is correct (Item, Record, or Regulatory record) |
| **Expected Result** | Zone 2: at least 5 labels (Communications-3Year, BooksRecords-6Year, Governance-6Year, Supervision-6Year, Configuration-6Year). Zone 3: add RegRecord-7Year, CFTC-5Year, ModelRisk-6Year |
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
| **Steps** | 1. Open **Purview portal** > **Data lifecycle management** > **Microsoft 365** > **Label policies**<br>2. Locate the FSI-AI-Governance-Retention policies<br>3. Verify each policy is **Enabled** (not in simulation mode)<br>4. Verify the **SharePoint location** includes the AI Governance site URL<br>5. For Zone 3: verify separate Zone 3 regulatory record policy exists |
| **Expected Result** | At least one active retention policy targets the AI Governance site with all required labels |
| **Pass Criteria** | Policy status = Enabled, SharePoint location includes AI Governance site |
| **Fail Criteria** | Policy missing, disabled, or not targeting the correct SharePoint site |
| **Evidence to Capture** | Screenshot of policy details showing enabled status and locations; PowerShell: `Get-RetentionCompliancePolicy | Where-Object { $_.Name -like '*FSI*' } | Select-Object Name, Mode, Enabled, SharePointLocation | Export-Csv` |

---

### TC-2.13-005 — Auto-Labeling Policy Operational

| Field | Detail |
|---|---|
| **Objective** | Verify auto-labeling policies are configured and applying retention labels to agent interaction logs |
| **Zone Applicability** | Zone 2 (recommended), Zone 3 (required) |
| **Preconditions** | PRE-02, TC-2.13-004 passed, allow 7+ days after label publishing |
| **Steps** | 1. Upload a test document to the `InteractionLogs` library with the text "Agent ID: TEST-001" and "Copilot interaction" in the content<br>2. Wait 24–48 hours for auto-labeling policy to process<br>3. Return to the document and check the **Retention label** column<br>4. Verify the label `FSI-Agent-Communications-3Year` (or the configured auto-label) has been applied |
| **Expected Result** | The uploaded document has the correct retention label automatically applied |
| **Pass Criteria** | Auto-applied label matches the expected label per the auto-labeling policy |
| **Fail Criteria** | No label applied after 48 hours, or wrong label applied |
| **Evidence to Capture** | Screenshot of document properties showing the auto-applied retention label with timestamp; document properties export |

---

### TC-2.13-006 — SEC 17a-4 Compliant Storage Configured (Zone 3 Only)

| Field | Detail |
|---|---|
| **Objective** | Verify WORM storage or audit-trail alternative is configured for Zone 3 agent records |
| **Zone Applicability** | Zone 3 only |
| **Preconditions** | PRE-02, Zone 3 deployment confirmed |
| **Steps** | **Option A (WORM):**<br>1. Open **Azure Portal** > **Storage accounts** > locate the FSI governance storage account<br>2. Navigate to **Containers** > `ai-governance-records`<br>3. Verify **Immutable blob storage** is configured with a time-based retention policy<br>4. Verify the policy is **Locked** (not unlocked)<br>5. Verify retention period ≥ 2190 days (6 years)<br>6. Attempt to delete a blob in the container — verify deletion is blocked<br><br>**Option B (Audit-trail):**<br>1. Review the audit-trail alternative documentation in WSPs<br>2. Verify DEO representation or DTP undertaking is on file<br>3. Verify Cohasset (or equivalent) attestation is current<br>4. Verify serialized indexing is operational |
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
| **Steps** | 1. Navigate to each governed library > **Settings** > **Versioning settings**<br>2. Verify **Create a version each time you edit a file** = Yes (Major versions)<br>3. Verify version limit is ≥ 500<br>4. Upload a test document, edit it, save — verify version 2.0 is created<br>5. Click **Version history** on the document and verify both versions are listed |
| **Expected Result** | Versioning enabled, edits create new versions, version history is viewable |
| **Pass Criteria** | Versioning on, version limit ≥ 500, test document shows version history |
| **Fail Criteria** | Versioning disabled, version limit too low, or version history not maintained |
| **Evidence to Capture** | Screenshot of versioning settings for each library; screenshot of test document version history |

---

### TC-2.13-008 — Copilot Studio Agent Version History Documented

| Field | Detail |
|---|---|
| **Objective** | Verify Microsoft Copilot Studio agent publish history and version information is captured and preserved |
| **Zone Applicability** | Zone 2, Zone 3 |
| **Preconditions** | Power Platform Admin role, agent deployed in a managed environment |
| **Steps** | 1. Open **Power Platform Admin Center** > **Environments** > select environment<br>2. Navigate to **Copilot Studio** > **Agents** > select agent<br>3. Review the **Publish history** — verify entries exist with timestamps and publisher identity<br>4. For agents in managed solutions: navigate to **Solutions** > select solution > review **Solution history**<br>5. Verify that an export of agent details (topics, actions, knowledge sources) has been saved to the `AgentConfigurations` library |
| **Expected Result** | Publish history visible with timestamped entries; agent details export saved to governance library |
| **Pass Criteria** | At least one publish record visible; latest agent export in AgentConfigurations library |
| **Fail Criteria** | No publish history, no agent export in governance library |
| **Evidence to Capture** | Screenshot of Copilot Studio publish history; screenshot of solution history (if applicable); file listing from AgentConfigurations library filtered by agent name |

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
| 6 | Agent inventory per environment CSV | §8 of PowerShell Setup | `agent-inventory-{env}-{stamp}.csv` | `manifest-2.13-{stamp}.csv` row 6 |
| 7 | Validation results CSV | §10 of PowerShell Setup | `validation-results-{stamp}.csv` | `manifest-2.13-{stamp}.csv` row 7 |
| 8 | Retention label creation evidence (JSON per label) | §4 of PowerShell Setup | `label-{name}-{stamp}.json` | Separate entries per label |
| 9 | Retention policy creation evidence (JSON per policy) | §5 of PowerShell Setup | `policy-{name}-{stamp}.json` | Separate entries per policy |
| 10 | PowerShell transcript | §1.3 of PowerShell Setup | `transcript-2.13-{stamp}.log` | Final transcript hash |
| 11 | Evidence manifest (master) | §9 of PowerShell Setup | `manifest-2.13-{stamp}.csv` | Self-referencing (manifest hash printed to console) |
| 12 | Site creation screenshot | Portal Walkthrough Step 1 | `evidence-2.13-site-creation.png` | Manual entry |
| 13 | Agent version screenshots | Portal Walkthrough Step 10 | `evidence-2.13-agent-version-*.png` | Manual entry |
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
   - Label policy published to AI Governance site

3. **Auto-labeling** (Zone 2+):
   - Auto-labeling policy: [Enabled / Not applicable]
   - Policy targets: [Library names]

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

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
