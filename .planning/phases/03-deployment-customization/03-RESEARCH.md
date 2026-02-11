# Phase 3 Research: Deployment & Customization

**Project:** Agent Usage & Performance Workbook (v15)
**Phase:** 3 — Deployment & Customization
**Researched:** 2026-02-11
**Overall Confidence:** HIGH

---

## 1. Existing Patterns (File Structure & Deployment Guide Format)

### CAA Deployment Guide Format (Established Pattern)

The CAA deployment guide at `docs/playbooks/advanced-implementations/conditional-access-automation/deployment-guide.md` (336 lines) establishes the project's deployment documentation pattern:

- **Header:** Status line, Related Controls, horizontal rule
- **Overview:** Brief description with estimated time
- **Phased deployment:** 5 numbered phases (Prerequisites, Schema, Module Install, Configuration, Validation)
- **Step-by-step within each phase:** `### Step N: Title` format with numbered portal navigation paths
- **Configuration tables:** Parameter/Value/Source tables for required inputs
- **Troubleshooting section:** Issue/Cause/Resolution table + Diagnostic Steps + Log Locations
- **Footer:** `*FSI Agent Governance Framework v1.2.38 - February 2026*`

Key formatting conventions:
- Portal navigation uses: "Navigate to [URL] > **Menu** > **Submenu**"
- Code blocks with language tags and inline comments
- `!!! note` admonitions for important caveats
- Tables for configuration items, parameters, troubleshooting

### Workbook Index (Current State)

The `docs/playbooks/advanced-implementations/agent-usage-workbook/index.md` already references Phase 3 deliverables as "Planned":

| Document | Status |
|----------|--------|
| Telemetry Schema Reference | Available |
| KQL Query Library | Planned (Phase 1) |
| **Deployment Guide** | **Planned (Phase 3)** |
| **Customization Guide** | **Planned (Phase 3)** |

### File Placement

Phase 3 deliverables go alongside existing files:

```
docs/playbooks/advanced-implementations/agent-usage-workbook/
├── index.md                 # EXISTS — update status table
├── telemetry-schema.md      # EXISTS (211 lines)
├── deployment-guide.md      # NEW — Plan 03-01 (DEP-01 + DEP-02)
└── customization-guide.md   # NEW — Plan 03-02 (FRM-03)
```

### mkdocs.yml Navigation Update

Current nav at mkdocs.yml lines 570-573:

```yaml
      - Agent Usage & Performance Workbook:
        - Overview: playbooks/advanced-implementations/agent-usage-workbook/index.md
        - Telemetry Schema Reference: playbooks/advanced-implementations/agent-usage-workbook/telemetry-schema.md
```

Needs two entries added:

```yaml
      - Agent Usage & Performance Workbook:
        - Overview: playbooks/advanced-implementations/agent-usage-workbook/index.md
        - Telemetry Schema Reference: playbooks/advanced-implementations/agent-usage-workbook/telemetry-schema.md
        - Deployment Guide: playbooks/advanced-implementations/agent-usage-workbook/deployment-guide.md
        - Customization Guide: playbooks/advanced-implementations/agent-usage-workbook/customization-guide.md
```

---

## 2. ARM Template Structure for Workbooks

### Resource Type & API Version

| Property | Value | Notes |
|----------|-------|-------|
| **Resource type** | `Microsoft.Insights/workbooks` | Standard for all Azure Monitor Workbooks |
| **API version** | `2018-06-17-preview` | Only stable API for workbook deployments |
| **Kind** | `shared` | Required for shared workbooks (default) |
| **Category** | `workbook` | Required property on the resource |

### Minimal ARM Template Structure

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "workbookDisplayName": {
      "type": "string",
      "defaultValue": "Agent Usage & Performance Workbook"
    },
    "workbookId": {
      "type": "string",
      "defaultValue": "[newGuid()]"
    },
    "applicationInsightsId": {
      "type": "string",
      "metadata": {
        "description": "Full resource ID of the Application Insights resource"
      }
    }
  },
  "resources": [
    {
      "type": "Microsoft.Insights/workbooks",
      "apiVersion": "2018-06-17-preview",
      "name": "[parameters('workbookId')]",
      "location": "[resourceGroup().location]",
      "kind": "shared",
      "properties": {
        "displayName": "[parameters('workbookDisplayName')]",
        "serializedData": "<ESCAPED JSON STRING of workbook content>",
        "version": "1.0",
        "sourceId": "[parameters('applicationInsightsId')]",
        "category": "workbook"
      }
    }
  ]
}
```

The `serializedData` property contains the entire workbook JSON (`src/agent-usage-workbook.json`) as a single escaped string. The `fallbackResourceIds` in the workbook JSON should reference `[parameters('applicationInsightsId')]`.

**Recommendation:** Document **both** approaches — manual import as primary (lower barrier), ARM template as optional for CI/CD pipelines.

---

## 3. RBAC Roles & ALM Scenario

### Relevant Azure Built-In Roles

| Role | Scope | What It Grants |
|------|-------|----------------|
| **Monitoring Reader** | Application Insights resource | Read all monitoring data (metrics, logs, workbook definitions) |
| **Application Insights Component Reader** | Application Insights resource | Read Application Insights component properties and data |
| **Reader** | Any | Read all resources including workbook definitions and App Insights data |
| **Workbook Reader** | Workbook resource | Read shared workbook definitions only (not the underlying data) |
| **Workbook Contributor** | Workbook resource | Save shared workbooks (required for deployers/editors) |
| **Log Analytics Reader** | Log Analytics workspace | Read log data (if App Insights is workspace-based) |

### Recommended RBAC Configuration for Workbook Consumers

Consumers need **two role assignments**:

| Assignment | Role | Scope | Purpose |
|-----------|------|-------|---------|
| 1 | **Monitoring Reader** | Application Insights resource | Execute KQL queries against telemetry data |
| 2 | **Workbook Reader** | Workbook resource or resource group | View the shared workbook definition |

**Alternative (simpler but broader):**

| Assignment | Role | Scope | Purpose |
|-----------|------|-------|---------|
| 1 | **Reader** | Resource group containing Application Insights | Covers both workbook viewing and data access |

### ALM Separation-of-Duties Scenario

This is the core scenario the workbook solves, per Control 2.8:

| Problem | Detail |
|---------|--------|
| **Gap** | PPAC Analytics tab requires Power Platform Admin or Environment Admin roles — production operators cannot access without elevated privileges |
| **Solution** | Application Insights workbook provides equivalent visibility using Azure RBAC. Operators get Monitoring Reader — no PPAC admin access needed |
| **Regulatory alignment** | Supports SOX 302/404 separation of duties; aids FINRA 3110 supervisory review without granting policy-change capability |

### RBAC by Persona (FSI-Specific)

| Persona | Roles Needed | Justification |
|---------|-------------|---------------|
| **Operations Team** | Monitoring Reader on App Insights | Real-time monitoring without PPAC admin access |
| **Compliance Officers** | Monitoring Reader + Purview Audit Reader | Workbook data + audit trail for regulatory review |
| **Executives** | Reader on workbook resource only | View shared workbook without direct data access |
| **Support Team** | Monitoring Reader on App Insights | Troubleshooting via workbook drill-downs |
| **Workbook Admin** | Workbook Contributor + Monitoring Reader | Deploy and modify workbook content |

---

## 4. Manual Import Workflow

### Portal Navigation Path

1. Navigate to [Azure Portal](https://portal.azure.com)
2. Go to **Application Insights** > select your resource
3. Click **Workbooks** (under Monitoring section)
4. Click **+ New**
5. Click **Advanced Editor** (`</>` icon in toolbar)
6. Set **Template Type** to **Gallery Template**
7. Clear default content, paste `agent-usage-workbook.json` contents
8. Click **Apply** — workbook preview renders
9. Click **Save** → configure Title, Subscription, Resource Group, Location
10. Click **Apply** to save

### Post-Import Configuration

1. **Update fallbackResourceIds:** Replace `{subscription-id}`, `{resource-group}`, `{app-insights-name}` placeholders with actual values
2. **Configure parameters:** Adjust MinutesSaved (default: 5) and HourlyRate (default: 75) per organization
3. **Verify telemetry flow** with verification KQL

---

## 5. Customization Patterns

### Workbook Item Types (from existing template)

| Type ID | Name | Count | Purpose |
|---------|------|-------|---------|
| 1 | Markdown | 4 | Headers, caveats, disclaimers |
| 3 | KQL Query | 23 | All data visualizations (Q01–Q23) |
| 9 | Parameters | 1 | Global parameters |
| 11 | Tab Links | 1 | Tab navigation (3 tabs) |
| 12 | Groups | 3 | Tab content containers |

### Zone-Aware Threshold Defaults (Zone 3)

| Metric | Green | Amber | Red | Query |
|--------|-------|-------|-----|-------|
| Resolution Rate | ≥ 80% | ≥ 60% | < 60% | Q06 |
| Connector Success Rate | ≥ 95% | ≥ 90% | < 90% | Q12 |
| Topic Completion Rate | ≥ 80% | ≥ 60% | < 60% | Q14 |
| GenAI Quality (inverted) | < 15% fallback | < 25% | ≥ 25% | Q20 |
| Dependency Health | ≥ 95% | ≥ 90% | < 90% | Q21 |
| Agent Health Summary | ≥ 80% | ≥ 60% | < 60% | Q23 |

### Recommended Thresholds by Zone

| Metric | Zone 1 (Personal) | Zone 2 (Team) | Zone 3 (Enterprise) |
|--------|-------------------|---------------|---------------------|
| Resolution Rate | ≥ 60% green | ≥ 70% green | ≥ 80% green |
| Connector Success | ≥ 85% green | ≥ 90% green | ≥ 95% green |
| Completion Rate | ≥ 60% green | ≥ 70% green | ≥ 80% green |
| GenAI Fallback | < 30% green | < 20% green | < 15% green |

### Adding Custom Panels

Conventions from the existing template:
- All queries include `customDimensions.designMode == "False"` filter
- All queries reference `{TimeRange}`, `{AgentFilter}`, `{ChannelFilter}` parameters
- Query names follow `query-QNN-kebab-case-description` pattern
- Regulatory comments precede each query (`// FINRA 4511: ...`)
- `timeContextFromParameter: "TimeRange"` links time picker to query

### Adding New Tabs

Three changes required:
1. Add tab link in type 11 item with new `cellValue`
2. Add type 12 group container with `conditionalVisibility` matching the new tab value
3. Insert the group in the `items` array before `fallbackResourceIds`

---

## 6. Prerequisites & Validation Checklist

### Prerequisites

**Azure Infrastructure:**
- Azure subscription with Contributor access (for workbook deployment)
- Resource group (same region as Application Insights)
- Application Insights resource (workspace-based, not classic)

**Copilot Studio Configuration:**
- Application Insights connection string configured per agent
- "Log activities" toggle enabled per agent
- (Optional) "Allow conversation transcripts" at environment level
- (Optional) "Log sensitive activity properties" per agent

**RBAC:**
- Monitoring Reader on Application Insights resource
- Workbook Reader (or Reader on resource group)

### Post-Deployment Validation

- Workbook opens without errors
- TimeRange parameter changes refresh visualizations
- AgentFilter dropdown populates with deployed agent names
- Session Volume Trend (Q01) shows data points
- Anomaly detection charts (Q17, Q19) render (need ≥14 days for meaningful patterns)
- Business Value Summary (Q08) reflects parameter values
- Monitoring Reader users can view workbook data (positive RBAC test)
- Users without Monitoring Reader see "access denied" (negative RBAC test)

---

## 7. Risks & Mitigations

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| User pastes JSON with placeholder resourceIds | High | Deployment guide explicitly addresses replacement; validation checklist includes data check |
| Insufficient RBAC | Medium | Document both Monitoring Reader AND Workbook Reader; include negative RBAC test |
| No telemetry data at deployment time | Medium | Prereqs checklist includes "send test message, verify events flow"; allow 5-10 min for ingestion |
| ARM serializedData escaping errors | Medium | Recommend manual import as primary; ARM as advanced option |
| Anomaly charts require 14-day baseline | Certain | Document expectation; Q17/Q19 need 2+ weeks of data |
| Zone metadata not in native telemetry | Certain | Document agent naming convention workaround; workbook provides agent-level filtering |
| FSI language violations | Low | Follow fsi-language-rules.instructions.md |

---

**No additional research required.** Existing codebase patterns and Azure Monitor documentation provide all needed technical details.

*Research completed: 2026-02-11*
*Sources: CAA deployment-guide.md (repo pattern), Azure Monitor Workbooks docs, Phase 1 research, src/agent-usage-workbook.json*
