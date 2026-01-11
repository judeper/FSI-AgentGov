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

## 8) Export + retention procedure

- Export cadence: weekly (Zone 3), monthly (Zone 2)
- Export storage: immutable evidence bucket / restricted SharePoint library
- Access: Compliance + Audit only
- Retention: align to your records policy

---

## 9) Approvals and changes

- **Owner:**
- **Approved by (Compliance):**
- **Approved by (Security):**
- **Approval date:**
- **Version:**
- **Change ticket/PR:**