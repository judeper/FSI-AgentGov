# Template: Purview Audit Query Pack (Copilot/Agent Governance)

**Purpose:** Standardize saved audit searches and export procedures so governance teams can reliably retrieve evidence for supervision, data access, and policy enforcement for Copilot/agent interactions.  
**Applies to:** Zone 2/3 agents (required for regulated), Zone 1 (recommended for baseline evidencing).  
**Microsoft grounding:** Purview “Audit (Standard)” automatically logs user interactions with Copilot/AI applications when auditing is enabled (no extra configuration needed beyond enabling auditing). [page:13]  
**Evidence grounding:** Copilot audit records include `AccessedResources` (with resource IDs/URLs, sensitivity label IDs, policy restriction details, and a boolean for cross-prompt injection detection) and include agent properties like `AgentId`, `AgentName`, and `AgentVersion`. [page:13]  
**Operational grounding:** Microsoft 365 admins can manage Copilot agents (enable/disable/assign/block/remove) via the Microsoft 365 admin center, which makes agent identity and lifecycle governance practical to evidence via an inventory + audit queries. [page:14]

---

## 1) Query pack metadata

- **Query pack name:** (e.g., “FSI-AgentGov — Copilot Interaction Evidence Pack”)
- **Owner:** (Compliance Ops / SecOps)
- **Applies to tenants/environments:** (Prod/Test)
- **Retention assumption:** (Audit Standard default; confirm if higher-tier retention is enabled)
- **Review cadence:** monthly

---

## 2) Core audit filters (recommended)

> Microsoft notes that to search for Copilot/AI audit scenarios, use the **Activities – operation names** filter and properties like `Operation`, `RecordType`, and `Workload`. [page:13]

### 2.1 User interactions: Microsoft Copilot interactions
- **Operation:** `CopilotInteraction` [page:13]
- **RecordType:** `CopilotInteraction` [page:13]
- **Workload:** `Copilot` [page:13]
- **Time window:** (e.g., last 7 days)
- **Export:** Yes (CSV/JSON)

**Use cases**
- Evidence of who used Copilot, when, where (AppHost), and what resources were accessed via `AccessedResources`. [page:13]

### 2.2 User interactions: Copilot Studio applications (custom copilots/agents)
Microsoft’s examples show Copilot Studio applications appear as `CopilotInteraction` with AppIdentity like `Copilot.Studio.<GUID>` and AppHost such as Teams. [page:13]

- **Operation:** `CopilotInteraction` [page:13]
- **RecordType:** `CopilotInteraction` [page:13]
- **AppHost:** Teams (or other) [page:13]
- **Post-filter (offline):** `AppIdentity` starts with `Copilot.Studio.` [page:13]

**Use cases**
- Evidence for custom agents built in Copilot Studio, including correlation to `AgentId`/`AgentName` where present. [page:13]

### 2.3 Admin activities: Copilot settings/plugins/workspaces
Microsoft notes audit logs are generated for administrator activities related to Copilot settings, plugins, promptbooks, or workspaces. [page:13]

- **Operation:** (select from “Microsoft 365 Copilot admin activities” list in Purview UI)
- **Workload/RecordType:** as applicable
- **Export:** Yes

**Use cases**
- Evidence of governance actions (policy changes, plugin enablement, settings changes).

---

## 3) Required export fields (for evidence packs)

When exporting, confirm the export includes (where available):
- `AgentId`, `AgentName`, `AgentVersion` [page:13]
- `AppHost`, `AppIdentity`, `RecordType`, `Operation` [page:13]
- `AccessedResources` array, including:
  - `ID`, `SiteUrl`, `Name`, `Type`, `Action`, `Status`
  - `SensitivityLabelId`
  - `PolicyDetails` (when blocked/restricted)
  - `XPIADetected` (cross prompt injection detection) [page:13]

---

## 4) Standard “evidence queries” (copy/paste checklist)

### Evidence Query A — “All Copilot interactions for a specific agent version”
**Goal:** Prove what changed after a release (agent drift / new version rollout).

- Time window: release date ± 7 days
- Filter: Operation = CopilotInteraction [page:13]
- Offline filter: `AgentId == <agent_id>` and `AgentVersion == <version>` [page:13]
- Output: list of interactions + accessed resources + policy blocks

### Evidence Query B — “All policy blocks for Restricted/Confidential content”
**Goal:** Prove DLP/label boundaries are enforced.

- Time window: last 30 days
- Filter: Operation = CopilotInteraction [page:13]
- Offline filter: any `AccessedResources[*].PolicyDetails` exists OR `SensitivityLabelId` in restricted label set [page:13]
- Output: blocked events list + resource IDs + policy rule identifiers

### Evidence Query C — “Cross Prompt Injection detections”
**Goal:** Show monitoring for prompt injection risks.

- Time window: last 30 days
- Filter: Operation = CopilotInteraction [page:13]
- Offline filter: any `AccessedResources[*].XPIADetected == true` [page:13]
- Output: XPIA event list + affected resources + response workflow

---

## 5) Correlation rules (tie audit to your governance artifacts)

Because audit logs include `AgentId`, `AgentName`, `AgentVersion`, link these to:
- Agent Inventory Entry (`templates/agent-inventory-entry.md`)
- Action Authorization Matrix (`templates/action-authorization-matrix.md`)
- Decision Logs (`templates/decision-log-schema.md`)
- Per-Agent Data Policy (`templates/per-agent-data-policy.md`)

This makes it possible to assemble exam-ready evidence without bespoke work each time. [page:13]

---

## 6) Saved search naming convention (recommended)

- `COPILOT-INT-<agent_name>-<agent_id>-LAST7D`
- `COPILOT-BLOCKS-<label_set>-LAST30D`
- `COPILOT-XPIA-LAST30D`
- `COPILOT-ADMIN-CHANGES-LAST90D`

---

## 7) Handling “web search” evidence

Microsoft notes you can identify if Copilot referenced the public web by checking `AISystemPlugin.Id` for the value `BingWebSearch` in the CopilotInteraction audit record when web search is enabled. [page:13]

- Evidence query: filter CopilotInteraction and offline filter on `AISystemPlugin.Id == BingWebSearch`. [page:13]

---

## 8) DLP correlation queries (Copilot policy location)

Microsoft Purview DLP supports a dedicated **Microsoft 365 Copilot and Copilot Chat** policy location. DLP events for this location appear in the Unified Audit Log with RecordType `DlpRuleMatch`.

### 8.1 DLP events for Copilot location

- **Operation:** Various DLP operations (`DlpRuleMatch`, `DlpPolicyMatch`)
- **RecordType:** `DlpRuleMatch` (55)
- **Workload:** `MicrosoftCopilot` or `Exchange` (depending on channel)
- **Time window:** (e.g., last 24 hours for daily operational report)
- **Export:** Yes (CSV/JSON)

**PowerShell Example:**

```powershell
# Export DLP events for Copilot policy location (last 24 hours)
$startDate = (Get-Date).AddDays(-1)
$endDate = Get-Date

$dlpEvents = Search-UnifiedAuditLog `
    -RecordType DlpRuleMatch `
    -StartDate $startDate `
    -EndDate $endDate `
    -ResultSize 5000

# Filter for Copilot-related DLP matches
$copilotDlp = $dlpEvents | Where-Object {
    $auditData = $_.AuditData | ConvertFrom-Json
    $auditData.PolicyDetails.PolicyName -match "Copilot" -or
    $auditData.Workload -eq "MicrosoftCopilot"
}

$copilotDlp | Export-Csv "DLP-Copilot-$(Get-Date -Format 'yyyy-MM-dd').csv" -NoTypeInformation
```

### 8.2 Daily deny event correlation query

To correlate CopilotInteraction deny events with DLP matches:

```powershell
# Step 1: Get CopilotInteraction events with blocks
$copilotBlocks = Search-UnifiedAuditLog `
    -RecordType CopilotInteraction `
    -StartDate $startDate `
    -EndDate $endDate `
    -ResultSize 5000 | Where-Object {
        $data = $_.AuditData | ConvertFrom-Json
        $data.AccessedResources | Where-Object {
            $_.Status -eq "failure" -or $_.PolicyDetails -ne $null
        }
    }

# Step 2: Get DLP events
$dlpMatches = Search-UnifiedAuditLog `
    -RecordType DlpRuleMatch `
    -StartDate $startDate `
    -EndDate $endDate `
    -ResultSize 5000

# Step 3: Correlate by UserId and timestamp window (±5 minutes)
# (Implement correlation logic in Power BI or offline processing)
```

### 8.3 Key DLP event fields

When exporting DLP events, confirm the export includes:

- `PolicyDetails.PolicyName`, `PolicyDetails.PolicyId`
- `SensitiveInfoTypesMatched` array
- `SensitivityLabelId` (if label-based rule)
- `Actions` (Block, Warn, Override)
- `UserId`, `Workload`, `CreationTime`

---

## 9) Daily operational export procedure

For organizations requiring daily deny event monitoring (Zone 2/3), implement scheduled exports:

### 9.1 Recommended export cadence

| Zone | CopilotInteraction | DLP Events | RAI Telemetry |
|------|-------------------|------------|---------------|
| **Zone 1** | Monthly | Monthly | Optional |
| **Zone 2** | Weekly | Weekly | Weekly |
| **Zone 3** | **Daily** | **Daily** | **Daily** |

### 9.2 Daily export automation

See the [Deny Event Correlation Report Playbook](../advanced-implementations/deny-event-correlation-report/index.md) for:

- PowerShell scripts for automated daily extraction
- KQL queries for Application Insights RAI telemetry
- Power BI template for multi-source correlation

### 9.3 Export storage recommendations

- **Azure Blob Storage** with immutable retention policy (SEC 17a-4 compatible)
- **SharePoint Compliance Library** with preservation hold
- **Azure Data Lake** for large-scale analytics

---

## 10) Export + retention procedure

- Export cadence: daily (Zone 3), weekly (Zone 2), monthly (Zone 1)
- Export storage: immutable evidence bucket / restricted SharePoint library
- Access: Compliance + Audit only
- Retention: align to your records policy

---

## 11) Approvals and changes

- **Owner:**
- **Approved by (Compliance):**
- **Approved by (Security):**
- **Approval date:**
- **Version:**
- **Change ticket/PR:**