# Verification & Testing: Control 1.26 - Agent File Upload and File Analysis Restrictions

**Last Updated:** May 2026
**Audience:** M365 administrators, AI Governance Lead, internal/external auditors

This playbook provides numbered test cases (`TC-1.26-XX`) with explicit Given / When / Then preconditions, an evidence-collection checklist, an attestation template, and a SHA-256-anchored auditor pack layout that supports SEC 17a-4(f) and FINRA 4511 preservation expectations.

---

## Test Cases

### TC-1.26-01 — Per-Agent Toggle State Matches Zone Policy

- **Given:** An agent classified as Zone *N* with documented approval state recorded in the per-agent inventory
- **When:** The reviewer opens *Microsoft Copilot Studio → \[Agent\] → Settings → Generative AI → File processing capabilities → File uploads* and reads the toggle state
- **Then:** The state matches the zone policy (Zone 1: any; Zone 2: Off unless approved; Zone 3: Off unless formally approved with risk assessment)
- **Pass Criteria:** Observed state == Expected state for every agent in the inventory
- **Evidence:** Screenshot of toggle state + row in `compliance-audit-<ts>.json` showing `Result = PASS`

### TC-1.26-02 — File Upload Blocked When Toggle Off

- **Given:** An agent with **File Upload = Off** that has been republished after the toggle change
- **When:** A test user opens the agent (Teams / web channel) and attempts to attach a `.pdf`
- **Then:** The agent does not present an attach control, or rejects the upload with an appropriate message
- **Pass Criteria:** No file is accepted; no upload entry appears in the Dataverse environment for the test agent (re-run `Get-AgentFileUploadInventory.ps1` and confirm no new knowledge file record for the test agent)
- **Evidence:** Screen recording or screenshot of upload attempt; Dataverse environment showing no new file record

### TC-1.26-03 — File Upload Accepted Only for Approved File Types

- **Given:** An agent with **File Upload = On** and **Allowed file types** restricted to `.pdf` only
- **When:** A test user uploads a `.pdf` (allowed) and then a `.docx` (disallowed)
- **Then:** The `.pdf` is accepted; the `.docx` is rejected
- **Pass Criteria:** Allowlist enforcement is observed at the agent level, independent of environment-level (Control 1.25) settings
- **Evidence:** Screenshot of accept and reject responses; PowerPlatformAdminActivity log entries

### TC-1.26-04 — Sensitivity Label Display in Responses (Preview Feature)

- **Given:** An agent with **File Upload = On**, Purview sensitivity labels published for the tenant, and Purview auto-labeling policies covering the Dataverse environment
- **When:** The reviewer uploads two test files as maker-uploaded knowledge: `confidential.pdf` (label: Confidential) and `highly-confidential.pdf` (label: Highly Confidential), then sends a test query that causes the agent to cite both files in its response
- **Then:** The agent response displays a shield icon showing **Highly Confidential** (the highest sensitivity label of cited content in that response)
- **Pass Criteria:** Per-response label shield is observed showing the most-restrictive label of cited content (this is a preview feature per Microsoft Learn — verify GA status before treating as Regulated-zone attestation evidence); allow up to 24 hours for new labeling policies
- **Evidence:** Screenshot of agent response showing the sensitivity label shield; Purview Activity Explorer entries for the uploads

### TC-1.26-05 — DLP Policy Triggered on Sensitive Content (Zone 2+)

- **Given:** A Zone 2 or Zone 3 agent with File Upload = On and a DLP policy in **Enforce** mode that includes US SSN as a Sensitive Information Type
- **When:** The reviewer uploads a synthetic test file containing 5+ formatted but non-real US SSNs (use `123-45-6789` style — never use real SSNs)
- **Then:** A DLP policy match is logged in *Purview → Data Loss Prevention → Activity explorer* and an alert is generated
- **Pass Criteria:** DLP match recorded within 24 hours; SOC alert delivered per configured channel
- **Evidence:** Activity Explorer screenshot; alert email/ticket reference

### TC-1.26-06 — Magic-Byte Inspection Blocks Renamed Executable (Zone 3)

- **Given:** A Zone 3 agent with Defender for Cloud Apps file policy configured for true-MIME inspection
- **When:** The reviewer uploads a Windows executable renamed `invoice.pdf` (magic bytes `MZ`, declared MIME `application/pdf`)
- **Then:** Defender for Cloud Apps quarantines the file and notifies the SOC distribution list
- **Pass Criteria:** Quarantine action recorded; file removed from the agent's Dataverse storage; alert raised
- **Evidence:** Defender XDR alert detail; Dataverse storage listing showing file absent or in quarantine state

### TC-1.26-07 — Per-Agent Inventory Accuracy (No Drift)

- **Given:** A documented per-agent inventory listing every agent's File Upload toggle state and approval reference
- **When:** The reviewer runs `Get-AgentFileUploadInventory.ps1` from the [PowerShell Setup](powershell-setup.md) playbook
- **Then:** The script output matches the documented inventory with zero drift
- **Pass Criteria:** Every agent in the script output is present in the inventory; every agent in the inventory is present in the script output; toggle states match
- **Evidence:** `agent-file-upload-inventory-<ts>.json` + manifest entry with SHA-256

### TC-1.26-08 — Dataverse Retention Policy Active (Zone 2+)

- **Given:** The agent's environment uses Dataverse to store uploaded knowledge files
- **When:** The reviewer queries Purview Data Lifecycle Management for retention policies covering the Dataverse location for the agent's environment
- **Then:** A retention policy is in scope with a retention period that meets the agent's record-keeping obligation (FINRA 4511: 6 years; SEC 17a-4: 6 years for most records, 3 years for some)
- **Pass Criteria:** Retention policy documented and active; Dataverse auditing enabled for the environment
- **Evidence:** Purview retention policy configuration export; auditing-enabled confirmation

### TC-1.26-09 — Toggle Change Is Logged and Attributable

- **Given:** A toggled change to the File Upload setting on any agent
- **When:** A SOC analyst queries the Power Platform admin activity log (or Sentinel mirror) for the agent ID
- **Then:** The change is recorded with timestamp, actor (UPN), and previous/new value
- **Pass Criteria:** Change attributable within 24 hours; recorded in immutable log
- **Evidence:** KQL query output (see queries below)

### TC-1.26-10 — Periodic Review Cadence Met

- **Given:** A per-agent inventory with documented next-review dates per zone (Zone 1: quarterly; Zone 2: monthly; Zone 3: weekly)
- **When:** The reviewer audits the **Last Reviewed** column for the past period
- **Then:** Every agent has been reviewed at the zone-appropriate cadence
- **Pass Criteria:** No agent overdue for review by more than one cadence interval
- **Evidence:** Inventory export with Last Reviewed dates; review meeting minutes

---

## Test Case Summary Table

| Test ID | Scenario | Zone | Expected Result | Pass/Fail |
|---------|----------|------|-----------------|-----------|
| TC-1.26-01 | Toggle state matches zone | All | Observed == Expected | |
| TC-1.26-02 | Upload blocked when toggle off | All | No file accepted | |
| TC-1.26-03 | Per-agent allowlist enforced | 2, 3 | Disallowed types rejected | |
| TC-1.26-04 | Sensitivity label display in responses (preview) | All | Response shield shows most-restrictive label | |
| TC-1.26-05 | DLP policy triggered | 2, 3 | DLP match logged + alert | |
| TC-1.26-06 | Magic-byte inspection blocks renamed exe | 3 | Quarantined + alert | |
| TC-1.26-07 | Inventory accuracy | All | Zero drift | |
| TC-1.26-08 | Dataverse retention policy active | 2, 3 | Policy in scope | |
| TC-1.26-09 | Toggle change logged + attributable | All | Logged in 24h | |
| TC-1.26-10 | Review cadence met | All | No agent overdue | |

---

## Evidence Collection Checklist

- [ ] `agent-file-upload-inventory-<ts>.json` (Script 1) with SHA-256 manifest entry
- [ ] `compliance-audit-<ts>.json` (Script 2) with PASS/WARN/FAIL counts and SHA-256
- [ ] `validation-summary-<ts>.json` (Script 4) with consolidated zone counts and SHA-256
- [ ] `before-snapshot-<ts>.json` and `mutation-results-<ts>.json` for every state change
- [ ] PowerShell session transcripts (`transcript-*.log`) for every script run
- [ ] Screenshot: per-agent File Upload toggle state (one per production agent — store under `maintainers-local/tenant-evidence/1.26/`, gitignored)
- [ ] Screenshot: agent rejecting an upload when toggle off (TC-1.26-02)
- [ ] Screenshot: agent with inherited Highly Confidential label (TC-1.26-04)
- [ ] Screenshot: Purview DLP Activity Explorer match (TC-1.26-05)
- [ ] Screenshot: Defender XDR quarantine alert for renamed executable (TC-1.26-06)
- [ ] Export: Dataverse environment security roles and retention policy configuration
- [ ] Approval records (ticket / record IDs) for every Zone 2/3 agent with File Upload enabled
- [ ] `manifest.json` indexing all artifacts by SHA-256 (canonical pattern per PowerShell baseline §4)

---

## Auditor Pack Layout

Bundle the following for handoff to internal audit, external audit, or regulatory examiner:

```
auditor-pack-1.26-<yyyymmdd>/
├── README.md                            ← This control summary + zone policy
├── manifest.json                        ← SHA-256 index of every file in the pack
├── evidence/
│   ├── agent-file-upload-inventory-<ts>.json
│   ├── compliance-audit-<ts>.json
│   ├── validation-summary-<ts>.json
│   ├── before-snapshot-<ts>.json        ← any state-change snapshots
│   └── mutation-results-<ts>.json
├── transcripts/
│   └── transcript-*.log                 ← PowerShell session transcripts
├── screenshots/                         ← Captured from maintainers-local/tenant-evidence/1.26/
│   ├── toggle-states/
│   ├── label-inheritance/
│   └── dlp-alerts/
├── approvals/
│   └── zone-2-3-enablement-records.csv  ← Ticket IDs and approver records
└── kql-evidence/
    └── activity-log-queries.json        ← Output from queries below
```

The `manifest.json` should follow the canonical PowerShell baseline §4 schema:

```json
[
  {
    "file": "evidence/agent-file-upload-inventory-20260415T143022Z.json",
    "sha256": "9F86D081884C7D659A2FEAA0C55AD015A3BF4F1B2B0B822CD15D6C15B0F00A08",
    "bytes": 12456,
    "generated_utc": "20260415T143022Z",
    "script": "Get-AgentFileUploadInventory",
    "control_id": "1.26"
  }
]
```

Land the auditor pack in WORM storage (Microsoft Purview Data Lifecycle retention lock or Azure Storage immutability policy) before sharing externally. Hashes published in the manifest support content-integrity verification at any later point in the records-retention period.

---

## Attestation Statement Template

```markdown
## Control 1.26 Attestation — Agent File Upload and File Analysis Restrictions

**Organization:** [Organization Name]
**Control Owner:** [Name / Role — typically AI Administrator]
**Reporting Period:** [YYYY-MM-DD] to [YYYY-MM-DD]
**Date of Attestation:** [YYYY-MM-DD]

I attest that, for the reporting period above:

1. The per-agent File Upload toggle state was reviewed against zone governance policy:
   - Zone 1 agents reviewed: [Count] — informal periodic review completed
   - Zone 2 agents reviewed: [Count] — [Count] enabled with documented approval; [Count] disabled
   - Zone 3 agents reviewed: [Count] — [Count] enabled under formal risk assessment; [Count] disabled (default deny)
2. Per-agent allowed-file-type allowlists were verified for least-privilege configuration on every Zone 2+ agent with File Upload = On
3. Sensitivity-label response shield display was tested for every Zone 2+ agent with File Upload = On (preview feature — verify GA status before treating as Regulated-zone attestation evidence)
4. DLP policies in Enforce mode covered every Zone 2+ environment hosting file-upload-enabled agents
5. Defender for Cloud Apps true-MIME content inspection was active for every Zone 3 agent
6. Dataverse environment security roles and Purview retention policies were verified for environments hosting agent knowledge files
7. Periodic review cadence was met: Zone 1 quarterly, Zone 2 monthly, Zone 3 weekly
8. Evidence was collected, hashed (SHA-256), and indexed in `manifest.json` per the FSI PowerShell Authoring Baseline §4
9. Evidence was landed in WORM storage consistent with SEC 17a-4(f) preservation requirements

**Total agents assessed:** [Count]
**Agents with File Upload enabled:** [Count]
**Compliant agents:** [Count]
**Non-compliant agents (open exceptions):** [Count]
**Open exceptions tracked in:** [Exception register reference]

**Signature:** _______________________
**Date:** _______________________
```

---

## Zone-Specific Testing Cadence

| Zone | Toggle Review | DLP Validation | Sensitivity Labels | Inventory Refresh | Dataverse Storage Review | KQL Activity Review |
|------|---------------|----------------|--------------------|-------------------|----------------------|---------------------|
| Zone 1 | Quarterly | N/A | Quarterly | Quarterly | Quarterly | Quarterly |
| Zone 2 | Monthly | Monthly | Monthly | Monthly | Monthly | Monthly |
| Zone 3 | Weekly | Weekly | Weekly | Weekly | Continuous (alert-driven) | Weekly + alert-driven |

---

## KQL Queries for Evidence

> **Note:** The schema and column names below reflect the Power Platform admin connector for Sentinel as of April 2026. Verify against your tenant — column names may vary between connector versions. Output rows should be exported (CSV/JSON) and added to the auditor pack's `kql-evidence/` folder with a SHA-256 manifest entry.

### Query 1 — Per-Agent File Upload Activity (Last 30 Days)

```kql
PowerPlatformAdminActivity
| where TimeGenerated > ago(30d)
| where Operation has_any ("FileUpload", "ChatbotFileUpload")
| project
    TimeGenerated,
    EnvironmentName = tostring(AdditionalProperties.EnvironmentName),
    AgentName       = tostring(AdditionalProperties.ChatbotName),
    UserPrincipalName = UserId,
    FileName        = tostring(AdditionalProperties.FileName),
    FileSizeBytes   = tolong(AdditionalProperties.FileSize),
    Operation
| order by TimeGenerated desc
```

### Query 2 — Toggle State Changes (Last 90 Days)

```kql
PowerPlatformAdminActivity
| where TimeGenerated > ago(90d)
| where Operation has_any ("UpdateChatbot", "ChatbotSettings")
| where AdditionalProperties has "FileUpload"
| project
    TimeGenerated,
    EnvironmentName = tostring(AdditionalProperties.EnvironmentName),
    AgentName       = tostring(AdditionalProperties.ChatbotName),
    ModifiedBy      = UserId,
    SettingChanged  = "FileUploadEnabled",
    NewValue        = tostring(AdditionalProperties.FileUploadEnabled)
| order by TimeGenerated desc
```

### Query 3 — Agents With Recent Upload Activity (Last 7 Days)

```kql
PowerPlatformAdminActivity
| where TimeGenerated > ago(7d)
| where Operation has "ChatbotFileUpload" and Operation has "Enabled"
| summarize
    LastUploadActivity = max(TimeGenerated),
    UploadCount        = count()
    by
    EnvironmentName = tostring(AdditionalProperties.EnvironmentName),
    AgentName       = tostring(AdditionalProperties.ChatbotName)
| order by UploadCount desc
```

### Query 4 — DLP Matches on Power Platform Uploads (Last 30 Days)

```kql
CloudAppEvents
| where Timestamp > ago(30d)
| where Application == "Power Platform"
| where ActionType has_any ("DLPRuleMatch", "DLPPolicyMatch")
| project
    Timestamp,
    AccountUpn,
    ActionType,
    ObjectName,
    PolicyName = tostring(RawEventData.PolicyName),
    SensitiveInfoType = tostring(RawEventData.SensitiveInfoType)
| order by Timestamp desc
```

---

[Back to Control 1.26](../../../controls/pillar-1-security/1.26-agent-file-upload-and-file-analysis-restrictions.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: June 2026 | Version: v1.6.2 | UI Verification Status: Current*
