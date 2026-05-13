# Playbook 3.14-A: Portal Walkthrough — Configuring Entra Diagnostic Settings and Verifying Telemetry in Admin Center

**Playbook ID:** 3.14-A
**Control:** 3.14 — Agent 365 Observability SDK and Custom Agent Telemetry
**Pillar:** Reporting
**Estimated Duration:** 45–90 minutes (initial configuration); 15–20 minutes (recurring verification)
**Required Role:** Entra Global Admin (diagnostic settings); AI Administrator (M365 Admin Center verification); Purview Compliance Admin (audit retention); Purview Audit Reader (audit search)
**Last Verified:** April 2026

---

!!! info "Preview Status"
    The Entra **agentSignIn** log type and **Is Agent = Yes** sign-in filter are in **Preview**. **MicrosoftServicePrincipalSignInLogs** as an Entra diagnostic setting is in **Public Preview** and requires explicit opt-in. Agent 365 Admin Center integration for SDK-instrumented agents requires Microsoft Agent 365 or Microsoft 365 E7 licensing (Agent 365 reached GA on May 1, 2026). All portal steps should be validated against current Entra and M365 Admin Center documentation before implementation.

---

## Overview

This playbook guides administrators through the portal-based configuration tasks required for Control 3.14 — specifically the Entra diagnostic settings that capture agent authentication telemetry, and the Admin Center verification steps that confirm SDK-instrumented custom agents are visible in the analytics dashboard. SDK installation procedures are covered in Playbook 3.14-B.

---

## Prerequisites

Before beginning, confirm:

- [ ] You have Entra Global Admin and Purview Compliance Admin role assignments (or equivalent scoped roles in your tenant).
- [ ] You have identified all custom (non-Microsoft-built) agents deployed in the tenant that require SDK instrumentation.
- [ ] A Log Analytics workspace exists in Azure for diagnostic log routing (or you will create one).
- [ ] WORM-compliant Azure Blob Storage is configured per Playbook 3.13-B (reused for agentSignIn log retention).
- [ ] Microsoft Agent 365 or Microsoft 365 E7 licensing is provisioned (for Admin Center metric verification).

---

## Part 1: Review Agent Sign-In Logs in Entra Admin Center

### Step 1.1: Access Entra Sign-In Logs

**1.1.1** Navigate to Entra Admin Center: `https://entra.microsoft.com`

**1.1.2** Sign in with Entra Global Admin or Entra Security Reader credentials.

**1.1.3** In the left navigation, go to: **Monitoring & health** > **Sign-in logs**

**1.1.4** The Sign-in logs page displays three tabs:
- User sign-ins (interactive)
- User sign-ins (non-interactive)
- **Service principal sign-ins** ← this is where agent sign-in activity appears

Select the **Service principal sign-ins** tab.

### Step 1.2: Apply the Agent Filter [Preview]

**1.2.1** On the Service principal sign-ins tab, locate the filter bar above the log table.

**1.2.2** Look for an "Is Agent" filter column or filter option. *(Note: This filter is in Preview and may not be available in all tenants or regions. If not visible, proceed to Step 1.3 and return to this step after the filter becomes available in your tenant.)*

**1.2.3** Set "Is Agent" = **Yes** to filter the view to agent-specific sign-in activity.

**1.2.4** Review the filtered results:
- **AppDisplayName**: The display name of the agent application
- **ServicePrincipalId**: The Entra service principal ID of the agent
- **ResourceDisplayName**: The resource the agent authenticated against
- **SignInDateTime**: Timestamp of the authentication event
- **Status**: Success or failure of the authentication attempt

**1.2.5** Look for new attributes in the log detail view by selecting an individual log entry:
- **AppOwnerTenantId**: The Entra tenant ID that owns the agent application
- **ResourceOwnerTenantId**: The Entra tenant ID that owns the accessed resource
- **SessionID**: A unique identifier correlating all events within a single agent session
- **SourceAppClientID**: The client ID of the originating agent application
- **UserAgent**: The client application string
- **ASN (Autonomous System Number)**: The network autonomous system number attributed to the agent's traffic origin

**1.2.6** Record the following in the governance log:
- Number of agent sign-in events in the last 7 days
- List of unique agent application names appearing in the filtered logs
- Any failed authentication events (Status = Failure) — these require immediate investigation

!!! note "New Attribute Availability"
    Not all new sign-in log attributes (AppOwnerTenantId, ResourceOwnerTenantId, ASN) may be populated for all agent types. Microsoft is rolling these out during the Preview period. If an attribute shows as blank, it does not necessarily indicate an error — the agent type may not yet support that attribute. Document which attributes are populated for your specific agent types.

---

## Part 2: Configure MicrosoftServicePrincipalSignInLogs Diagnostic Setting [Public Preview]

This diagnostic setting creates an additional log stream capturing first-party service-to-service token requests between Microsoft-owned services. It is distinct from the standard service principal sign-in logs and must be explicitly opted into.

### Step 2.1: Access Diagnostic Settings

**2.1.1** In Entra Admin Center, navigate to: **Monitoring & health** > **Diagnostic settings**

**2.1.2** Select **+ Add diagnostic setting**

### Step 2.2: Configure the Diagnostic Setting

**2.2.1** In the Name field, enter a descriptive name: `FSI-AgentGov-ServicePrincipalSignInLogs`

**2.2.2** In the **Logs** section, locate and check:
- [ ] **MicrosoftServicePrincipalSignInLogs** (Public Preview — may appear with a Preview badge)

Also consider enabling complementary log categories for comprehensive agent telemetry:
- [ ] **ServicePrincipalSignInLogs** (if not already configured in another diagnostic setting)
- [ ] **AuditLogs** (captures agent-related Entra configuration changes)

**2.2.3** In the **Destination details** section, configure routing destinations:

**Destination 1 — Log Analytics Workspace** (for real-time query and alerting):
- Check **Send to Log Analytics workspace**
- Select your Azure Subscription
- Select or create a Log Analytics workspace (e.g., `law-fsi-agentgov`)

**Destination 2 — Storage Account** (for long-term WORM retention — Zone 3 requirement):
- Check **Archive to a storage account**
- Select your Azure Subscription
- Select the WORM-compliant storage account configured in Playbook 3.13-B
- Retention: set to **0** (meaning "keep indefinitely" — rely on the immutability policy for retention governance, not the storage account's own retention setting)

**2.2.4** Select **Save**

!!! warning "Single Diagnostic Setting Per Log Category"
    Azure allows only one diagnostic setting per log category per destination type for Entra logs. If a diagnostic setting for `ServicePrincipalSignInLogs` already exists in your tenant (configured by another admin), you must edit the existing setting to add `MicrosoftServicePrincipalSignInLogs` rather than creating a duplicate. Creating a duplicate will result in an error.

### Step 2.3: Verify Diagnostic Setting Activation

**2.3.1** Allow 15–30 minutes for the diagnostic setting to activate.

**2.3.2** Navigate to your Log Analytics workspace in the Azure Portal.

**2.3.3** Select **Logs** in the workspace blade.

**2.3.4** Run the following KQL query to confirm log ingestion:

```kql
// Verify MicrosoftServicePrincipalSignInLogs are flowing to Log Analytics
MicrosoftServicePrincipalSignInLogs
| where TimeGenerated > ago(1h)
| summarize Count = count()
| project LogCount = Count, Status = iff(Count > 0, "FLOWING", "NO DATA YET")
```

Expected result: Count > 0 if service-to-service agent authentication activity has occurred in the last hour. If Count = 0 after 30 minutes, see Troubleshooting Playbook 3.14-D.

---

## Part 3: Verify agentSignIn Log Retention Configuration

### Step 3.1: Check Purview Audit Retention Policies

**3.1.1** Navigate to Microsoft Purview compliance portal: `https://compliance.microsoft.com`

**3.1.2** Go to: **Audit** > **Audit retention policies** (or Data lifecycle management > Retention policies if audit-specific retention is managed there in your tenant configuration)

**3.1.3** Confirm that a retention policy exists covering agent sign-in and agent session audit records.

**3.1.4** Verify the retention duration:
- FINRA Rule 4511 minimum: **6 years** for most broker-dealer books and records (validate with counsel for record-type-specific durations under SEC 17a-4)
- If the policy shows a shorter duration (e.g., 1 year default for E3 licenses), create a new retention policy as shown in Step 3.2.

### Step 3.2: Create Agent-Specific Audit Log Retention Policy

**3.2.1** In Microsoft Purview: Audit > Audit retention policies > + Create

**3.2.2** Policy name: `FSI-AgentGov-AgentSignIn-6yr`

**3.2.3** Policy description: `Retains agent sign-in and agent session audit records for 6 years to help meet FINRA Rule 4511 and SEC Rule 17a-4 recordkeeping requirements for broker-dealer activities.`

**3.2.4** Record types: Select all applicable agent-related record types. Look for:
- `AgentSignIn` (if available as a record type — Preview)
- `AIPSensitivityLabelAction` (if agents are applying sensitivity labels)
- Any other agent activity record types visible in your tenant

**3.2.5** Duration: **10 years** (set to 10 years rather than exactly 6 to provide a buffer against mid-period policy modification; this exceeds FINRA 4511 requirements without conflicting with them)

**3.2.6** Priority: set to a value that places this policy above the default audit log retention policy (lower number = higher priority in Purview retention policy evaluation)

**3.2.7** Save the policy.

!!! note "Purview Record Type Availability"
    The `AgentSignIn` record type is in Preview and may not yet be available as a selectable option in Purview audit retention policies for all tenants. If it is not visible, configure the retention policy to cover the broadest available set of agent-related record types and plan to update the policy when `AgentSignIn` becomes GA. Document this gap in the IT governance register.

---

## Part 4: Verify SDK-Instrumented Agents in M365 Admin Center

After SDK implementation (Playbook 3.14-B), return to this step to confirm that custom agents are visible in the Admin Center.

### Step 4.1: Confirm Agent Registry Visibility

**4.1.1** Navigate to M365 Admin Center > Agents > All Agents.

**4.1.2** For each custom agent that has been instrumented with the Agent 365 Observability SDK, confirm the agent appears in the All Agents list.

**4.1.3** Select the agent to open its detail view. Confirm:
- Agent status: Active
- Publisher type: Organization (for internally built agents)
- Owner: assigned
- Platform: matches the deployment platform (Azure AI Foundry, etc.)

**4.1.4** Record each confirmed custom agent in the SDK implementation registry (document: agent name, SDK implementation date, Admin Center visibility confirmation date, confirming admin).

### Step 4.2: Confirm Metric Contribution [Requires Agent 365 / E7 licensing]

**4.2.1** Navigate to Agents > Overview.

**4.2.2** Note the Total Sessions count.

**4.2.3** Run a test agent invocation using the custom agent (a simple "hello" query is sufficient).

**4.2.4** Wait 30–60 minutes for telemetry to propagate. Refresh the Overview page.

**4.2.5** Confirm the Total Sessions count has incremented by at least 1 compared to the pre-test value.

!!! info "Metric Propagation Delay"
    Agent 365 metrics are not real-time. Expect up to 60 minutes for a new agent invocation to appear in the Total Sessions count. For Exception Rate, propagation of exception events may take up to 4 hours. Do not interpret absence of immediate metric change as an SDK integration failure.

---

## Part 5: Verify Purview Audit Log Ingestion

### Step 5.1: Search Purview Audit Log for Agent Sessions

**5.1.1** Navigate to Microsoft Purview: `https://compliance.microsoft.com` > **Audit** > **New search**

**5.1.2** Configure search parameters:
- Date range: last 24 hours (or since SDK implementation)
- Activities — Record types: search for "Agent" to find applicable activity types
- User: optionally filter to the service principal account used by the custom agent

**5.1.3** Run the search.

**5.1.4** Confirm results contain records associated with your SDK-instrumented agent.

**5.1.5** Select an individual audit record and review the detail pane. Confirm the record contains:
- Workload identifier indicating the source agent
- Operation/Activity type (e.g., AgentSession, AgentToolCall)
- Timestamp
- User or service principal identity

**5.1.6** Document the search result count and a sample record identifier in the governance log.

Expected result: At least one audit record is present for each SDK-instrumented agent that has been invoked since SDK implementation.

### Step 5.2: Confirm Telemetry Completeness

**5.2.1** Compare the number of agent sessions you know occurred (from your test invocations or operational monitoring) to the number of Purview audit records found.

**5.2.2** If Purview records are significantly fewer than expected sessions, a telemetry gap exists. Refer to Troubleshooting Playbook 3.14-D.

---

## Part 6: Complete the Governance Log Entry

Upon completion of this walkthrough, document in the governance log:

- Date and time of configuration/verification activity
- Administrator name and role
- MicrosoftServicePrincipalSignInLogs diagnostic setting: configured / verified / not yet available (with reason)
- agentSignIn log filter: verified / not yet available (with reason)
- Purview retention policy: retention duration confirmed, policy name, record types covered
- Custom agents confirmed in Admin Center Registry: list of agent names
- Total Sessions baseline count (for future comparison)
- Purview audit search result count
- Any gaps identified and remediation plan with owner and due date

---

[Back to Control 3.14](../../../controls/pillar-3-reporting/3.14-agent-365-observability-sdk.md) | [PowerShell and SDK Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

*Updated: April 2026 | Version: v1.6.2 | UI Verification Status: Current*
