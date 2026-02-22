# Agent Usage & Performance Workbook — Deployment Guide

[Playbooks](../../index.md) > Advanced Implementations > [Agent Usage & Performance Workbook](index.md) > Deployment Guide

**Status:** February 2026 — FSI-AgentGov v1.2.48
**Related Controls:** 3.1, 3.2, 3.3, 3.7, 3.8, 2.8, 2.9

---

## Overview

This guide provides end-to-end deployment instructions for the Agent Usage & Performance Workbook — an Azure Monitor Workbook that surfaces Copilot Studio agent telemetry from Application Insights. The workbook addresses the ALM separation-of-duties gap identified in Control 2.8: PPAC Analytics requires Power Platform Admin or Environment Admin roles, but this workbook uses Azure RBAC (`Monitoring Reader`) to provide equivalent visibility without elevated privileges.

**Estimated Time:** 30–60 minutes

**Workbook Source:** `agent-observability-foundation/src/agent-usage-workbook.json` (in [FSI-AgentGov-Solutions](https://github.com/judeper/FSI-AgentGov-Solutions))

---

## Prerequisites Checklist

Before proceeding, confirm the following prerequisites are met:

- [ ] Azure subscription with **Contributor** access to a target resource group
- [ ] Application Insights resource (workspace-based, not classic)
- [ ] Copilot Studio agents with Application Insights connection string configured
- [ ] **Log activities** enabled per agent in Copilot Studio (Settings > Advanced > Log activities)
- [ ] At least one completed production conversation (not test canvas)
- [ ] Telemetry verified in `customEvents` table (`BotMessageReceived` events visible)

!!! warning "Test Canvas Traffic"
    Conversations in the Copilot Studio test canvas emit telemetry with `designMode = "True"`. The workbook filters these out by default. Verify that production traffic (via Teams, SharePoint, or other channels) is generating events before proceeding.

---

## Step 1: Configure RBAC Access

### Option A: Read-Only Access for Workbook Consumers (DEP-01)

Workbook consumers need two role assignments to view workbook data:

| Assignment | Role | Scope | Purpose |
|-----------|------|-------|---------|
| 1 | Monitoring Reader | Application Insights resource | Execute KQL queries against telemetry |
| 2 | Workbook Reader | Workbook resource or resource group | View the shared workbook definition |

!!! tip "Simplified Alternative"
    Assigning the **Reader** role at the resource group level covers both Monitoring Reader and Workbook Reader permissions. Use this approach when fine-grained RBAC scoping is not required.

#### Persona-Based RBAC Assignments

| Persona | Roles Needed | Justification |
|---------|-------------|---------------|
| Operations Team | Monitoring Reader on App Insights | Real-time monitoring without PPAC admin privileges |
| Compliance Officers | Monitoring Reader + Purview Audit Reader | Workbook data combined with audit trail |
| Executives | Reader on workbook resource | View shared workbook only |
| Support Team | Monitoring Reader on App Insights | Troubleshooting via drill-down visualizations |
| Workbook Admin | Workbook Contributor + Monitoring Reader | Deploy and modify workbook definitions |

#### Azure CLI Commands

```bash
# Assign Monitoring Reader on Application Insights resource
az role assignment create \
  --assignee "<user-or-group-object-id>" \
  --role "Monitoring Reader" \
  --scope "/subscriptions/{sub-id}/resourceGroups/{rg}/providers/microsoft.insights/components/{app-insights-name}"

# Assign Workbook Reader on resource group
az role assignment create \
  --assignee "<user-or-group-object-id>" \
  --role "Workbook Reader" \
  --scope "/subscriptions/{sub-id}/resourceGroups/{rg}"
```

#### PowerShell Equivalent

```powershell
# Assign Monitoring Reader on Application Insights resource
New-AzRoleAssignment -ObjectId "<object-id>" `
  -RoleDefinitionName "Monitoring Reader" `
  -Scope "/subscriptions/{sub-id}/resourceGroups/{rg}/providers/microsoft.insights/components/{app-insights-name}"

# Assign Workbook Reader on resource group
New-AzRoleAssignment -ObjectId "<object-id>" `
  -RoleDefinitionName "Workbook Reader" `
  -Scope "/subscriptions/{sub-id}/resourceGroups/{rg}"
```

#### ALM Separation-of-Duties Context

This RBAC model directly addresses the separation-of-duties gap documented in Control 2.8:

- **Problem:** The PPAC Analytics tab requires Power Platform Admin or Environment Admin roles to access agent usage data.
- **Solution:** The Application Insights workbook provides equivalent visibility using Azure RBAC (`Monitoring Reader`), which carries no Power Platform administrative privileges.
- **Regulatory alignment:** Supports SOX 302/404 separation of duties; aids FINRA 3110 supervisory review requirements.

### Option B: Workbook Administrator Access

For initial deployment and ongoing workbook modifications, assign:

- **Workbook Contributor** — Create, edit, and delete workbook definitions
- **Monitoring Reader** — Execute KQL queries during workbook authoring

---

## Step 2: Import Workbook (Manual)

### 2.1: Open Application Insights Workbooks

1. Navigate to [Azure Portal](https://portal.azure.com)
2. Go to **Application Insights** > select your resource
3. Under **Monitoring**, click **Workbooks**

### 2.2: Open Advanced Editor

1. Click **+ New**
2. Click the **Advanced Editor** icon (`</>`)
3. Set **Template Type** to **Gallery Template**

### 2.3: Paste Workbook JSON

1. Download or copy the contents of `agent-observability-foundation/src/agent-usage-workbook.json` from the [FSI-AgentGov-Solutions](https://github.com/judeper/FSI-AgentGov-Solutions) repository
2. Paste the JSON into the editor, replacing any existing content
3. Click **Apply**

### 2.4: Save Workbook

1. Click **Save As** (disk icon)
2. Configure:
   - **Title:** `Agent Usage & Performance Workbook`
   - **Subscription:** Select target subscription
   - **Resource Group:** Select target resource group
   - **Location:** Select preferred region
3. Click **Save**

### 2.5: Configure Parameters

After saving, update the following workbook parameters:

| Parameter | Default Value | Action Required |
|-----------|--------------|-----------------|
| `fallbackResourceIds` | Placeholder resource ID | Replace with your Application Insights resource ID: `/subscriptions/{sub-id}/resourceGroups/{rg}/providers/microsoft.insights/components/{name}` |
| `MinutesSaved` | 5 | Adjust per your organization's estimated time savings per agent interaction |
| `HourlyRate` | 75 | Adjust per your organization's blended hourly labor rate |

!!! note "Parameter Customization"
    The `MinutesSaved` and `HourlyRate` parameters drive the Business Value Summary calculations. These should reflect your organization's estimates — work with business stakeholders to determine appropriate values. Default values are conservative starting points.

---

## Step 3: Import Workbook (ARM Template — Optional)

For organizations that prefer infrastructure-as-code deployments, use an ARM template to deploy the workbook programmatically.

### 3.1: ARM Template Structure

Create an ARM template file (e.g., `arm-workbook-template.json`) with the following structure:

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
        "serializedData": "<paste escaped workbook JSON here>",
        "sourceId": "[parameters('applicationInsightsId')]",
        "category": "workbook"
      }
    }
  ]
}
```

!!! warning "JSON Escaping"
    The `serializedData` field requires the workbook JSON to be escaped as a string value. Use a JSON escaping tool or the manual import method (Step 2) if escaping proves problematic.

### 3.2: Deploy via Azure CLI

```bash
az deployment group create \
  --resource-group "<resource-group>" \
  --template-file "arm-workbook-template.json" \
  --parameters applicationInsightsId="/subscriptions/{sub-id}/resourceGroups/{rg}/providers/microsoft.insights/components/{name}"
```

### 3.3: Deploy via PowerShell

```powershell
New-AzResourceGroupDeployment `
  -ResourceGroupName "<resource-group>" `
  -TemplateFile "arm-workbook-template.json" `
  -applicationInsightsId "/subscriptions/{sub-id}/resourceGroups/{rg}/providers/microsoft.insights/components/{name}"
```

---

## Step 4: Post-Deployment Validation

After deployment, verify the workbook is functioning correctly:

### Validation Checklist

1. Workbook opens without errors in Azure Portal
2. **TimeRange** parameter changes refresh all visualizations
3. **AgentFilter** dropdown populates with deployed agent names
4. **ChannelFilter** dropdown shows active channels (`msteams`, `directline`, etc.)
5. Session Volume Trend (Usage tab) shows data points
6. Active Users over Time chart renders
7. Performance metrics display latency values (if production traffic exists)
8. Business Value Summary reflects `MinutesSaved` and `HourlyRate` parameter values
9. Operational Health tab renders (anomaly charts need ≥14 days baseline data)
10. **Monitoring Reader** users can view all workbook data (positive RBAC test)
11. Users **without** Monitoring Reader receive access denied (negative RBAC test)
12. **Workbook Reader** users can open the workbook definition

!!! note "Anomaly Detection Baseline"
    Anomaly detection charts (Usage Anomaly Detection, Error Rate Anomaly Detection) require approximately 14 days of historical data to establish meaningful baselines. These charts may appear empty or show limited patterns immediately after deployment. This is expected behavior.

### Telemetry Verification Query

Run this KQL query in Application Insights > Logs to confirm telemetry is flowing:

```kql
customEvents
| where timestamp > ago(1h)
| where customDimensions.designMode == "False"
| summarize count() by name
| order by count_ desc
```

Expected event types include `BotMessageReceived`, `BotMessageSend`, `BotMessageUpdate`, and `LuisResult` (or equivalent intent events).

---

## ALM Separation-of-Duties Scenario

This workbook directly addresses a governance gap for organizations subject to separation-of-duties requirements:

| Aspect | Detail |
|--------|--------|
| **Gap** | PPAC Analytics tab requires Power Platform Admin or Environment Admin roles |
| **Impact** | Production operators cannot access usage data without elevated privileges that may violate separation-of-duties policies |
| **Solution** | Application Insights workbook provides equivalent visibility using Azure RBAC (`Monitoring Reader`) |
| **Regulatory alignment** | Supports SOX 302/404 separation of duties; aids FINRA 3110 supervisory review |
| **Control reference** | Control 2.8 — Access Control and Segregation of Duties |

!!! tip "Implementation Caveat"
    While this workbook helps meet separation-of-duties requirements by removing the need for PPAC admin roles, organizations should still document the RBAC assignments and include them in periodic access reviews as part of their broader identity governance program.

---

## Troubleshooting

### Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| Workbook shows no data | Telemetry not configured or only test canvas traffic | Verify Application Insights connection string in Copilot Studio; confirm `designMode` filter excludes test traffic |
| "Access denied" for workbook viewer | Missing RBAC role assignments | Assign Monitoring Reader on App Insights resource + Workbook Reader on resource group |
| AgentFilter dropdown empty | No production conversations recorded | Send a test message via Teams or SharePoint channel (not Copilot Studio test canvas) |
| Parameter changes don't refresh | Browser caching or unsaved workbook | Refresh browser; verify workbook is saved (not in draft state) |
| ARM deployment fails | Invalid `serializedData` escaping | Use manual import method (Step 2); verify JSON is properly escaped in ARM template |
| Empty anomaly charts | Insufficient historical data (<14 days) | Allow 14+ days of telemetry accumulation for anomaly baseline calculation |
| Business Value shows $0 | `MinutesSaved` or `HourlyRate` set to 0 | Update parameter defaults in workbook settings (Step 2.5) |
| Workbook Contributor can't save | Insufficient permissions on resource group | Assign Contributor on the resource group or scope Workbook Contributor to the workbooks resource type |

### Diagnostic Steps

1. **Verify telemetry flow:** Run `customEvents | take 10` in Application Insights > Logs
2. **Check RBAC assignments:** Azure Portal > Application Insights > Access control (IAM) > Check access
3. **Verify workbook JSON:** Open Advanced Editor > validate JSON syntax and structure
4. **Check parameter bindings:** Enter Edit mode > click each parameter > verify the backing query returns data

---

*FSI Agent Governance Framework v1.2.48 - February 2026*
