# Control 3.14 — Verification & Testing: Agent 365 Observability SDK and Custom Agent Telemetry

**Playbook ID:** 3.14-C
**Control:** 3.14 — Agent 365 Observability SDK and Custom Agent Telemetry
**Pillar:** Reporting
**Estimated Duration:** 2–3 hours
**Required Role:** Entra Global Admin or Entra Security Reader (sign-in log review); AI Administrator (Admin Center verification); SOC Analyst (Defender verification); Purview Audit Reader (Purview verification); Microsoft Copilot Studio Agent Author / Application developer (SDK-level verification)
**Last Verified:** April 2026

---

!!! info "Testing Scope"
    This playbook verifies the end-to-end telemetry chain: from agent invocation through SDK instrumentation, through telemetry export, to final ingestion in Microsoft Purview (compliance records), Microsoft Defender (security alerting), and the M365 Admin Center (supervisory dashboard). Each test must be completed for every custom agent before that agent is considered compliant with Control 3.14.

---

## Overview

The Agent 365 Observability SDK creates a telemetry chain with four key destinations:

```
Agent Invocation → SDK Instrumentation → Agent 365 Export Service
       ↓                                         ↓
  Local Logging               ┌─────────────────────────────────┐
                               │  M365 Admin Center              │
                               │  Microsoft Purview              │
                               │  Microsoft Defender             │
                               │  Log Analytics (via Entra Diag) │
                               └─────────────────────────────────┘
```

This playbook tests each link in this chain and produces a verification certificate confirming the telemetry chain is intact for each custom agent.

---

## Pre-Test Preparation

### Environment Setup

Before running tests, ensure the following are in place:

1. The custom agent under test has the SDK installed and `ENABLE_A365_OBSERVABILITY_EXPORTER=true` set.
2. The agent's Entra app registration has been confirmed active.
3. You have access to all four verification destinations:
   - M365 Admin Center (Entra Global Admin or AI Administrator)
   - Microsoft Purview portal (Purview Audit Reader)
   - Microsoft Defender portal (Entra Security Reader or above)
   - Azure Log Analytics workspace (Log Analytics Reader)
4. The agent under test can be invoked manually with a simple test query.

### Baseline Metrics (Record Before Testing)

Before invoking any test agent sessions, record the current baseline values:

| Metric | Value Before Testing | Source |
|---|---|---|
| Admin Center Total Sessions | | M365 Admin Center > Agents > Overview |
| Admin Center Exception Rate | | M365 Admin Center > Agents > Overview |
| Purview Audit Records (24h) | | Purview > Audit > Search |
| Defender Active Incidents | | Defender portal > Incidents |
| Log Analytics MicrosoftServicePrincipalSignInLogs (1h) | | Log Analytics > Logs |

---

## Test 1: SDK Instrumentation Confirmation

**Test Objective**: Confirm the SDK is installed, initialized, and running in the production agent environment.

**Test Steps**:

**T1.1 — Package Verification**

For Python agents:
```bash
pip show microsoft-agents-a365
```
Expected: Package metadata displayed, including version number.

For .NET agents:
```bash
dotnet list package | grep "Microsoft.Agents.A365"
```
Expected: All required packages listed with version numbers.

For JavaScript agents:
```bash
npm list @microsoft/agents-a365-observability
```
Expected: Package listed with version number.

**T1.2 — Environment Variable Verification**
```bash
# Confirm the exporter is enabled
echo $ENABLE_A365_OBSERVABILITY_EXPORTER
```
Expected: Output is `true`. Any other value (including blank) means the exporter is disabled and telemetry will not flow.

**T1.3 — Startup Log Verification**

Review the agent's application logs at startup. The SDK should log an initialization message similar to:

```
Agent 365 Observability initialized: [your-agent-service-name]
Exporter enabled: true
```

If this log line is absent, the SDK `config.configure()` or `AddAgentObservability()` call was not reached during startup. Review the agent initialization sequence.

**T1.4 — Token Acquisition Test**

Confirm the SDK's token resolver can acquire a token. Test by running the token resolver function in isolation:

```python
# Python test
from your_agent_module import get_token_resolver
resolver = get_token_resolver()
token = resolver()
assert len(token) > 0, "Token acquisition failed"
print(f"Token acquired successfully (length: {len(token)} characters)")
```

Expected: Token acquired without error. A failed token acquisition blocks all telemetry export.

**Evidence to Record**:
- Package version output (copy/paste from terminal)
- Environment variable confirmation
- Startup log snippet showing SDK initialization
- Token acquisition test result

Pass Criteria: All four sub-tests pass with expected outputs.

---

## Test 2: Agent Session Telemetry (Admin Center Verification)

**Test Objective**: Confirm that a test agent invocation results in a Total Sessions increment in the M365 Admin Center dashboard.

**Test Steps**:

**T2.1 — Pre-Test Baseline**
Record the current Total Sessions value from M365 Admin Center > Agents > Overview.

**T2.2 — Execute Test Agent Invocation**
Send a simple, well-defined test query to the custom agent. Use a query that:
- Is easily identifiable in logs (e.g., "OBSERVABILITY-SDK-TEST-[timestamp]")
- Completes successfully without error
- Does not involve sensitive data

**T2.3 — Wait for Propagation**
Agent 365 metrics have an ingestion delay. Wait **60 minutes** after the test invocation before checking.

**T2.4 — Verify Session Count**
Navigate to M365 Admin Center > Agents > Overview. Confirm:
- Total Sessions count has increased by at least 1 compared to the baseline
- Agent Runtime has increased (the test session added to total runtime)

**T2.5 — Verify Agent Visibility in Registry**
Navigate to Agents > All Agents. Confirm the custom agent under test appears in the agent list.

**T2.6 — Verify No Exception Rate Impact**
Confirm the Exception Rate metric has not declined as a result of the test invocation (since the test query completed successfully, no exception should have been recorded).

**Evidence to Record**:
- Screenshot of Admin Center Overview (before and after) showing Total Sessions values
- Timestamp of test invocation
- Timestamp of post-test Admin Center screenshot
- Exception Rate values (before and after — should be unchanged or improved)

Pass Criteria: Total Sessions increases after test invocation. Agent appears in registry. Exception Rate unaffected.

Fail Criteria: Total Sessions unchanged after 2+ hours. Refer to Troubleshooting Playbook 3.14-D, Issue 2.1.

---

## Test 3: Microsoft Purview Audit Log Verification

**Test Objective**: Confirm that agent session telemetry is being ingested into the Microsoft Purview Unified Audit Log.

**Test Steps**:

**T3.1 — Execute Named Test Session**
If not already done in Test 2, execute a test agent invocation with an identifiable query string. Record the exact timestamp.

**T3.2 — Wait for Purview Ingestion**
Purview audit log ingestion may take 30–90 minutes. Wait at least 90 minutes after the test invocation before searching.

**T3.3 — Purview Audit Search**

Navigate to Microsoft Purview portal > Audit > New search:
- **Start date**: 2 hours before the test invocation
- **End date**: current time
- **Activities**: Search for "Agent" in the activity filter; select all agent-related activities available
- **User**: optionally filter to the service principal account of the test agent

Run the search and review results.

**T3.4 — Validate Audit Record Content**

Select an audit record from the search results that corresponds to the test session. Confirm the detail pane contains:
- [ ] Workload: identifying the source agent or Agent 365 service
- [ ] Operation/Activity: an agent session or agent tool call type
- [ ] Timestamp: consistent with the test invocation time
- [ ] Actor/User: the agent service principal or the invoking user identity
- [ ] Additional details: session ID, agent name, or other identifying attributes

**T3.5 — Retention Policy Confirmation**

Navigate to Purview > Data lifecycle management > Retention policies (or Audit > Audit retention policies). Confirm the retention policy covering agent records shows:
- Status: Active
- Duration: consistent with FINRA 4511 / SEC 17a-4 (typically a 6-year minimum for broker-dealer records / 2,190 days)
- Record types: includes agent-related record types

**Evidence to Record**:
- Screenshot of Purview Audit search results showing agent records
- Screenshot of individual audit record detail view
- Screenshot or export of retention policy configuration showing duration
- Record count from the search results

Pass Criteria: At least one Purview audit record found corresponding to the test session. Retention policy confirmed at the firm's regulatory minimum (typically 6+ years for broker-dealer records).

Fail Criteria: No Purview records found after 90 minutes. Refer to Troubleshooting Playbook 3.14-D, Issue 3.1.

---

## Test 4: Microsoft Defender Integration Verification

**Test Objective**: Confirm that agent exception events generate detectable alerts or incidents in Microsoft Defender.

!!! warning "Controlled Exception Test"
    This test intentionally triggers an agent exception (error) to verify that Defender receives and surfaces the anomaly. Coordinate with the IT Security team before executing this test to prevent alert fatigue or false incident escalations. Notify the Security Operations Center (SOC) that a controlled test exception will be generated.

**Test Steps**:

**T4.1 — SOC Notification**
Notify the SOC and Security team that a controlled agent exception test will be executed. Provide:
- Test start time
- Agent name
- Expected exception type (intentional test exception)
- Test duration

**T4.2 — Execute Test Exception**
Trigger an intentional exception in the test custom agent. Methods include:
- Providing an invalid input that the agent is designed to reject with an error
- Temporarily setting an incorrect API endpoint that will cause a tool call failure
- Using the agent's built-in test exception method if the SDK provides one

Record the exact timestamp of the intentional exception.

**T4.3 — Restore Agent State**
Immediately restore the agent to its correct configuration if a configuration change was made to trigger the exception.

**T4.4 — Check Defender for Agent Exception Alert**

Navigate to Microsoft Defender portal: `https://security.microsoft.com`

Go to: Incidents & alerts > Alerts

Filter:
- Time range: last 2 hours
- Category: optionally filter to "Application" or search for "agent"

Search for an alert corresponding to the test exception. The alert may be titled with the agent service name, agent session ID, or a generic exception descriptor.

**T4.5 — Verify Alert Details**

If an alert is found, select it and confirm the detail view shows:
- Agent or service principal identifier
- Exception event timestamp consistent with the test
- Session ID (if available in the alert detail)
- Recommended remediation action

**T4.6 — Document Result**

If an alert is found: record the alert ID, title, severity, and timestamp as evidence.

If no alert is found after 4 hours: document as a potential Defender integration gap. Note: Defender alert generation for agent exceptions depends on the type and severity of the exception and Defender's anomaly detection configuration. Some exception types may not generate immediate alerts but will be visible in the Defender advanced hunting tables. Proceed to T4.7 if no alert is found.

**T4.7 — Advanced Hunting Query (if no automatic alert)**

In Defender portal > Advanced hunting, run the following KQL query:

```kql
// Search for agent-related events in Defender hunting tables
// Adjust table names and columns per your Defender license and schema
CloudAppEvents
| where TimeGenerated > ago(4h)
| where Application contains "agent" or ActionType contains "agent"
| project TimeGenerated, Application, ActionType, AccountDisplayName, AdditionalFields
| order by TimeGenerated desc
| take 50
```

If no records appear in CloudAppEvents, also check:
```kql
IdentityLogonEvents
| where TimeGenerated > ago(4h)
| where Application contains "agent" or isnotempty(AccountName)
| where Protocol == "OAuth2"
| project TimeGenerated, Application, AccountName, ActionType, FailureReason
| order by TimeGenerated desc
| take 50
```

**Evidence to Record**:
- SOC notification documentation (email or ticket number)
- Timestamp of test exception
- Screenshot of Defender alert (if found), including alert ID and severity
- Advanced hunting query results (if used)
- Result: Alert found / Not found (with explanation if not found)

Pass Criteria: A Defender alert or advanced hunting record is found corresponding to the test exception.

Partial Pass: Advanced hunting shows the exception event but no automatic alert was generated. Document Defender detection rule configuration as a gap item.

Fail Criteria: No evidence of the exception event in Defender or advanced hunting after 4 hours. Refer to Troubleshooting Playbook 3.14-D.

---

## Test 5: Entra Sign-In Log Agent Attribution Verification

**Test Objective**: Confirm that the agent's authentication events are visible in Entra sign-in logs with the "Is Agent = Yes" attribute.

**Test Steps**:

**T5.1 — Execute Agent Invocation**
Execute a test agent invocation (same as used in previous tests, or a new one).

**T5.2 — Access Entra Sign-In Logs**
Navigate to Entra Admin Center > Monitoring & health > Sign-in logs > Service principal sign-ins.

**T5.3 — Apply Agent Filter**
If the "Is Agent = Yes" filter is available in your tenant (Preview), apply it. If not available, filter by the agent's service principal application ID.

**T5.4 — Locate Test Session**
Filter the date/time range to the period around the test invocation. Look for an entry with:
- AppDisplayName matching the test agent's registered application name
- SignInDateTime matching the test invocation time

**T5.5 — Verify New Attributes**
Select the sign-in log entry and expand the detail view. Confirm presence of:
- [ ] AppOwnerTenantId (Preview — may be blank if not yet populated)
- [ ] ResourceOwnerTenantId (Preview — may be blank)
- [ ] SessionID (should be populated — correlates to the agent session)
- [ ] SourceAppClientID (should match the agent's Entra app client ID)
- [ ] UserAgent (should identify the SDK or agent framework)
- [ ] ASN (Preview — network attribution; may be blank)

**T5.6 — Document Attribute Availability**
For each attribute listed in T5.5, document whether it was populated or blank. Blank attributes during the Preview period are expected for some agent types; document this in the IT governance register as a known limitation pending Microsoft GA rollout.

**T5.7 — Log Analytics Correlation**

If MicrosoftServicePrincipalSignInLogs are flowing to Log Analytics (confirmed in Playbook 3.14-A), run the following verification query:

```kql
// Correlate Entra agent sign-in to Log Analytics
// Adjust where clause to match your agent's application ID
MicrosoftServicePrincipalSignInLogs
| where TimeGenerated > ago(2h)
| where ServicePrincipalId == "YOUR_AGENT_SERVICE_PRINCIPAL_ID"
| project TimeGenerated, ServicePrincipalName, ResourceDisplayName, ResultType, CorrelationId
| order by TimeGenerated desc
```

Expected: Records visible in Log Analytics corresponding to the test invocation.

**Evidence to Record**:
- Screenshot of Entra sign-in log entry with agent sign-in attributes visible
- List of which new attributes were populated vs. blank
- Log Analytics query result (if applicable)

Pass Criteria: Agent authentication events visible in service principal sign-in logs. SessionID attribute populated.

---

## Test 6: agentSignIn Log Retention Compliance Test

**Test Objective**: Confirm that agentSignIn log records are retained in WORM-compliant storage and that the retention duration satisfies FINRA Rule 4511 (6-year minimum).

**Test Steps**:

**T6.1 — WORM Storage Verification**
```powershell
# Verify immutability policy on agent log retention storage
$Policy = Get-AzStorageContainerImmutabilityPolicy `
    -ResourceGroupName "rg-fsi-agentgov-records" `
    -StorageAccountName "YOUR_STORAGE_ACCOUNT" `
    -ContainerName "agent-inventory-exports"

Write-Host "Immutability period: $($Policy.ImmutabilityPeriodSinceCreationInDays) days"
Write-Host "Policy state: $($Policy.State)"
```

Expected:
- ImmutabilityPeriodSinceCreationInDays = 2190 (6 years) or greater
- State = "Locked" (for Zone 3 production environments)

**T6.2 — Blob File Presence Verification**
```powershell
# Verify agent log files are present in WORM storage
$Context = (Get-AzStorageAccount -ResourceGroupName $rg -Name $sa).Context
$Blobs = Get-AzStorageBlob -Container "agent-inventory-exports" -Context $Context

Write-Host "Files in WORM storage: $($Blobs.Count)"
$Blobs | Select-Object Name, LastModified, Length | Format-Table -AutoSize
```

Expected: Files present with date-stamped names and recent LastModified timestamps.

**T6.3 — Purview Retention Policy Verification**
Navigate to Microsoft Purview > Audit > Audit retention policies. Confirm the policy configured in Playbook 3.14-A is:
- Status: Active
- Duration: 2,555 days (7 years) or greater *(the playbook recommends 10 years = 3,650 days for buffer)*
- Record types: covers agent-related activity types

**Evidence to Record**:
- PowerShell output showing immutability policy state and period
- Screenshot of Purview audit retention policy showing duration
- Blob file listing from WORM storage

Pass Criteria: Immutability policy is Locked (Zone 3) with period ≥ 2,190 days. Purview retention policy is Active with duration ≥ 2,555 days.

---

## Verification Certificate

Complete one Verification Certificate per custom agent tested. Retain as an examination artifact.

---

**Control 3.14 VERIFICATION CERTIFICATE**

Agent Name: ____________________________
Agent Entra Service Principal ID: ____________________________
Agent Platform: ____________________________
SDK Language and Version: ____________________________
Testing Date: ____________________________
Tester Name and Role: ____________________________

| Test | Result | Notes |
|---|---|---|
| Test 1: SDK Instrumentation Confirmation | PASS / FAIL | |
| Test 2: Admin Center Total Sessions | PASS / FAIL / N/A (Frontier) | |
| Test 3: Purview Audit Log Ingestion | PASS / FAIL | |
| Test 4: Defender Exception Alerting | PASS / PARTIAL / FAIL | |
| Test 5: Entra Sign-In Log Attribution | PASS / FAIL | |
| Test 6: WORM Retention Compliance | PASS / FAIL | |

**Overall Result**:
- [ ] COMPLIANT — All applicable tests passed; agent meets Control 3.14 requirements
- [ ] CONDITIONALLY COMPLIANT — Minor gaps identified; remediation plan attached; re-test required within 30 days
- [ ] NON-COMPLIANT — Material gaps identified; agent must be remediated before continued operation (Zone 3) or within 90 days (Zone 2)

Tester Signature: ____________________________
Date: ____________________________

Reviewed by Compliance Officer: ____________________________
Date Reviewed: ____________________________

*This certificate may constitute a business record subject to FINRA Rule 4511 and SEC Rule 17a-4 when associated with regulated activity. Retention should align with firm policy and the applicable regulatory minimum (typically 6 years for broker-dealer records).*

---

[Back to Control 3.14](../../../controls/pillar-3-reporting/3.14-agent-365-observability-sdk.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell and SDK Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
