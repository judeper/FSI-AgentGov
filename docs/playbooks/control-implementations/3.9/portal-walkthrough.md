# Control 3.9: Microsoft Sentinel Integration - Portal Walkthrough

> This playbook provides step-by-step portal configuration guidance for [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md).

---

## Prerequisites

- Microsoft Sentinel workspace deployed
- Microsoft Sentinel Contributor or higher role
- Log Analytics Workspace Contributor
- Microsoft 365 E5 or Microsoft Sentinel standalone license

---

## Step 1: Deploy Microsoft Sentinel Workspace

**Portal Path:** Azure Portal > Microsoft Sentinel

1. Navigate to [Azure Portal](https://portal.azure.com)
2. Search for "Microsoft Sentinel"
3. Click **+ Create**
4. Select or create a Log Analytics workspace
5. Click **Add** to enable Sentinel

---

## Step 2: Connect Data Sources

**Portal Path:** Microsoft Sentinel > Configuration > Data connectors

Connect the following data connectors for agent monitoring:

| Connector | Data Type | Setup |
|-----------|-----------|-------|
| **Microsoft 365 Defender** | Security alerts, incidents | One-click setup |
| **Microsoft Entra ID** | Sign-in and audit logs | Enable diagnostic settings |
| **Office 365** | Exchange, SharePoint, Teams activity | Enable |
| **Microsoft Defender for Cloud Apps** | Cloud app activity | API connection |
| **Azure Activity** | Azure resource operations | Enable |

**Enable Microsoft 365 Defender Connector:**

1. Navigate to **Data connectors**
2. Search for "Microsoft 365 Defender"
3. Click **Open connector page**
4. Click **Connect incidents & alerts**
5. Enable all event types

---

## Step 3: Configure Analytics Rules for Agents

**Portal Path:** Microsoft Sentinel > Configuration > Analytics

Create custom analytics rules for AI agent monitoring:

**Rule 1: Unusual Agent Data Access**

| Setting | Value |
|---------|-------|
| Name | Unusual Agent Data Access Pattern |
| Tactics | Discovery, Collection |
| Severity | Medium |
| Query | See KQL below |
| Run frequency | 5 minutes |
| Lookup data | 1 hour |

**Rule 2: Agent DLP Violation**

| Setting | Value |
|---------|-------|
| Name | AI Agent DLP Policy Violation |
| Tactics | Exfiltration |
| Severity | High |
| Query | See KQL below |
| Run frequency | 5 minutes |

**Rule 3: After-Hours Agent Activity**

| Setting | Value |
|---------|-------|
| Name | Agent Activity Outside Business Hours |
| Tactics | Initial Access |
| Severity | Low |
| Query | See KQL below |

---

## Step 4: Create Agent Activity Workbook

**Portal Path:** Microsoft Sentinel > Threat management > Workbooks

Create a workbook with these sections:

| Section | Visualizations |
|---------|---------------|
| **Overview** | Total agents, active today, alerts by severity |
| **Activity Timeline** | Agent interactions over time |
| **Top Agents** | Most active agents ranked |
| **Data Access** | Documents/sources accessed by agents |
| **Anomalies** | Flagged unusual activity |
| **DLP Events** | Policy violations by agent |

---

## Step 5: Configure Automated Responses

**Portal Path:** Microsoft Sentinel > Configuration > Automation

Create automation rules:

| Rule | Trigger | Actions |
|------|---------|---------|
| Suspend High-Risk Agent | High severity alert on agent | Disable agent, notify security |
| Escalate DLP Violation | DLP alert for Zone 3 agent | Create incident, email compliance |
| Log Agent Incident | Any agent-related alert | Log to incident tracker |

---

## Step 6: Configure Copilot Studio Application Insights (Custom Telemetry Path)

**Portal Path:** Copilot Studio > Agent > Settings > Advanced

If using the Application Insights custom telemetry path for conversation-level monitoring (see Control 3.9 "Custom Integration for Comprehensive Telemetry"), configure the following prerequisites:

### 6a: Enable Application Insights in Agent Settings

1. Open [Copilot Studio](https://copilotstudio.microsoft.com)
2. Select the target agent
3. Navigate to **Settings** (gear icon) > **Advanced**
4. Click **Application Insights**
5. Enter the Application Insights **Connection String**
6. Enable **"Log activities"** — this enables basic telemetry flow
7. Enable **"Log sensitive activity properties"** — this includes actual conversation text, user IDs, and node details in the telemetry

!!! warning "Without Step 7"
    If only "Log activities" is enabled, Application Insights will receive events but conversation content fields will be empty or sanitized. This does not satisfy FINRA 4511 recordkeeping requirements.

### 6b: Verify Environment-Level Transcript Setting

1. Open [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
2. Navigate to **Environments** > select the target environment
3. Click **Settings** > **Product** > **Features**
4. Verify **"Allow conversation transcripts"** is **On**

!!! note "Scope"
    This setting primarily controls Dataverse transcript storage, but when disabled it can also block downstream telemetry flow to Application Insights.

### 6c: Verify Data Flow

After enabling both settings, verify conversation data appears in Application Insights:

1. Open [Azure Portal](https://portal.azure.com) > **Application Insights** > select the linked resource
2. Navigate to **Logs**
3. Run a test query to confirm conversation content is present:

    ```kql
    customEvents
    | where timestamp > ago(1h)
    | where name in ("BotMessage", "UserMessage")
    | extend text = tostring(customDimensions.text)
    | project timestamp, name, text
    | take 10
    ```

4. Confirm the `text` column contains actual conversation content (not empty values)

---

## Step 7: Set Up Hunting Queries

**Portal Path:** Microsoft Sentinel > Threat management > Hunting

Create saved hunting queries:

| Query Name | Purpose |
|------------|---------|
| Agent Data Exfiltration Patterns | Look for bulk data access |
| Dormant Agent Reactivation | Detect unused agents starting |
| Cross-Zone Data Movement | Agent accessing higher-zone data |
| Failed Authentication Patterns | Repeated agent auth failures |

---

## Step 8: Configure Incident Management

**Portal Path:** Microsoft Sentinel > Threat management > Incidents

Configure incident workflow:

1. Set auto-assignment rules for agent incidents
2. Configure severity escalation timeline
3. Enable entity mapping for agents
4. Set up integration with incident tracking (Control 3.4)

---

## Validation

After completing the configuration, verify:

1. [ ] Microsoft Sentinel workspace deployed and accessible
2. [ ] Required data connectors enabled and ingesting data
3. [ ] Analytics rules created and enabled for agent monitoring
4. [ ] Agent activity workbook displaying data correctly
5. [ ] Automation rules triggering on test alerts
6. [ ] Application Insights receiving conversation content (if custom telemetry path configured)
7. [ ] Hunting queries saved and returning expected results
8. [ ] Incident assignment workflow functioning

**Expected Result:** Agent security events flow to Sentinel, analytics rules generate alerts for suspicious activity, and automated responses execute as configured.

---

---

[Back to Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: January 2026 | Version: v1.2*
