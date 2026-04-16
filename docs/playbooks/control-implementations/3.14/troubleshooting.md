# Playbook 3.14-D: Troubleshooting — Resolving SDK Integration and Telemetry Ingestion Issues

**Playbook ID:** 3.14-D
**Control:** 3.14 — Agent 365 Observability SDK and Custom Agent Telemetry
**Pillar:** Reporting
**Last Verified:** March 2026

---

!!! info "Preview Instability"
    The Agent 365 Observability SDK and associated Entra log features are in Preview. Many issues encountered during implementation reflect the evolving state of Preview features rather than configuration errors. Before spending significant time troubleshooting, check the Microsoft 365 Message Center and the official SDK repository changelog for known issues and recent breaking changes. When in doubt, open a FastTrack or Microsoft Support ticket referencing the Preview feature name.

---

## Overview

This playbook addresses the most common issues encountered during Agent 365 Observability SDK implementation, telemetry pipeline configuration, and verification testing. Issues are organized by the component in the telemetry chain where the failure occurs. Each issue includes diagnostic commands and resolution steps.

---

## Diagnostic Reference: Telemetry Chain Failure Points

When telemetry is missing from a destination, use this chain to isolate where the failure is occurring:

```
[Agent Runtime]
     ↓
[SDK Initialization]       ← Issue Category 1
     ↓
[Token Acquisition]        ← Issue Category 2
     ↓
[Agent 365 Export Service] ← Issue Category 3
     ↓
[Admin Center Metrics]     ← Issue Category 4
[Purview Audit Log]        ← Issue Category 5
[Microsoft Defender]       ← Issue Category 6
[Entra Sign-In Logs]       ← Issue Category 7
```

---

## Issue Category 1: SDK Initialization Failures

### Issue 1.1: SDK package import fails with ModuleNotFoundError (Python)

**Symptom**:
```
ModuleNotFoundError: No module named 'microsoft_agents_a365'
```

**Probable Causes**:
- Package was installed in the wrong Python virtual environment
- Package was not installed in the container image used for production deployment

**Resolution**:
1. Confirm the active Python environment: `which python` and `which pip`
2. Confirm the package is installed in the correct environment: `pip show microsoft-agents-a365`
3. If the agent runs in a Docker container: confirm the `pip install microsoft-agents-a365` line is in the Dockerfile, after any `RUN pip install` statements that change the base environment.
4. Reinstall in the correct environment: `pip install microsoft-agents-a365 --force-reinstall`

---

### Issue 1.2: SDK initialization call raises a ValueError about missing configuration

**Symptom**:
```python
ValueError: service_name must be provided and cannot be empty
```

**Resolution**:
1. Confirm that `service_name` and `service_namespace` are being passed to `config.configure()` as non-empty strings.
2. Confirm that the environment variables `AGENT_SERVICE_NAME` and `AGENT_SERVICE_NAMESPACE` are set in the runtime environment.
3. Check for leading/trailing whitespace in environment variable values (a common issue with values copied from documentation).
4. Set a fallback default in the code rather than relying solely on environment variables in pre-production testing.

---

### Issue 1.3: .NET SDK AddAgentObservability() throws NullReferenceException

**Symptom**: Application crashes during startup with `NullReferenceException` in `AddAgentObservability`.

**Probable Causes**:
- The `TokenResolver` delegate is null
- `ServiceName` is null or empty in the options configuration

**Resolution**:
1. Confirm the `TokenResolver` property is explicitly assigned in the options lambda — it does not have a default implementation.
2. Confirm `ServiceName` is read from configuration and that the configuration key exists:
   ```csharp
   options.ServiceName = builder.Configuration["AgentObservability:ServiceName"]
       ?? throw new InvalidOperationException("AgentObservability:ServiceName must be configured");
   ```
3. If using managed identity, verify the Azure resource (App Service, Container App) has a system-assigned or user-assigned managed identity enabled in the Azure Portal.

---

## Issue Category 2: Token Acquisition Failures

### Issue 2.1: Token acquisition fails with AADSTS700016 (Application not found)

**Symptom**:
```
MSAL AADSTS700016: Application with identifier '[client-id]' was not found in the directory '[tenant-id]'.
```

**Resolution**:
1. Verify the Client ID in the SDK configuration matches the Application (Client) ID of the Entra app registration (not the Object ID).
2. Verify the Tenant ID is correct for the target tenant.
3. Confirm the Entra app registration exists and has not been deleted: Entra Admin Center > App registrations > search by client ID.
4. Confirm the app registration is in the same tenant as the agent's runtime environment.

---

### Issue 2.2: Token acquisition fails with AADSTS65001 (User or admin has not consented)

**Symptom**:
```
MSAL AADSTS65001: The user or administrator has not consented to use the application.
```

**Resolution**:
1. Navigate to Entra Admin Center > App registrations > [your agent app] > API permissions.
2. Confirm `https://agent365.microsoft.com/.default` scope (or the specific Agent 365 scopes) are added.
3. Select **Grant admin consent for [tenant name]** and confirm.
4. Wait 5–10 minutes for consent propagation, then retry token acquisition.

---

### Issue 2.3: DefaultAzureCredential fails with "No credential available" in production

**Symptom**:
```
Azure.Identity.CredentialUnavailableException: DefaultAzureCredential failed to retrieve a token from the included credentials.
```

**Probable Causes**:
- The Azure resource (App Service, Container App, VM) does not have a managed identity enabled
- The managed identity is not assigned the correct permissions for Agent 365

**Resolution**:
1. Enable managed identity on the Azure resource: Azure Portal > [your resource] > Identity > Status = On > Save.
2. Note the Object ID of the system-assigned managed identity.
3. In Entra Admin Center, assign the managed identity the required API permissions using the service principal. (Managed identity API permission assignment requires PowerShell — it cannot be done through the portal UI.):
   ```powershell
   # Assign API permissions to managed identity
   $ManagedIdentityObjectId = "YOUR_MANAGED_IDENTITY_OBJECT_ID"
   $GraphServicePrincipal    = Get-MgServicePrincipal -Filter "appId eq '00000003-0000-0000-c000-000000000000'"

   # Find the required role on the Agent 365 service principal
   # (Replace with actual Agent 365 application ID)
   $A365ServicePrincipal = Get-MgServicePrincipal -Filter "appId eq 'AGENT365_APP_ID'"
   ```
4. Alternatively, switch to ClientSecretCredential for non-Azure environments and retrieve the secret from Azure Key Vault.

---

## Issue Category 3: Export Service Connectivity Issues

### Issue 3.1: Telemetry export silently fails — no data in Admin Center or Purview

**Symptom**: SDK initializes without error, agent invocations complete, but no data appears in Admin Center metrics or Purview audit log after waiting the expected propagation delay.

**Probable Causes**:
- `ENABLE_A365_OBSERVABILITY_EXPORTER` environment variable is not set to `true`
- Network or firewall is blocking outbound connections to the Agent 365 export endpoint
- The agent application is using a Preview SDK version with a known export bug

**Diagnostic Steps**:

1. Confirm the environment variable:
   ```bash
   echo $ENABLE_A365_OBSERVABILITY_EXPORTER
   # Expected output: true
   ```
   If blank or `false`, set the variable and restart the agent.

2. Test network connectivity to the Agent 365 service:
   ```bash
   # Test HTTPS connectivity to Agent 365 export endpoint
   curl -v --max-time 10 https://agent365.microsoft.com
   # A 401 Unauthorized response confirms network connectivity is working.
   # A timeout or DNS failure indicates a network block.
   ```

3. Check for firewall or proxy blocks: the Agent 365 Observability SDK requires outbound HTTPS (port 443) access to `*.microsoft.com` endpoints. Review your organization's firewall rules and proxy configuration.

4. Enable verbose SDK logging (Python):
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   # Run the agent and capture debug output for telemetry export events
   ```

**Resolution**:
1. Set `ENABLE_A365_OBSERVABILITY_EXPORTER=true` and restart the agent.
2. If a firewall is blocking traffic: work with Network Security to add Agent 365 export endpoints to the outbound allowlist. Consult the SDK documentation for the specific endpoints required.
3. If the SDK version has a known export bug: upgrade to the latest Preview version per the SDK repository release notes.

---

### Issue 3.2: Export works but data takes more than 4 hours to appear

**Symptom**: Telemetry export appears to be working (no errors in logs) but data takes 4–8 hours to appear in Admin Center and Purview, making real-time monitoring impractical.

**Probable Causes**:
- Preview-period telemetry pipeline latency (known behavior)
- High-volume tenant with metric aggregation delay

**Resolution**:
1. This is expected behavior during the Preview period. The Agent 365 telemetry pipeline is not real-time — it is batch-aggregated on a rolling schedule.
2. For near-real-time monitoring, supplement Admin Center metrics with direct queries against Log Analytics (Entra diagnostic logs provide faster visibility than the Admin Center aggregations).
3. Configure Log Analytics alert rules for immediate exception detection rather than relying on the Admin Center dashboard refresh cycle.
4. Document the ingestion delay in the firm's written supervisory procedures and set review cadences that account for the delay (e.g., review yesterday's data, not today's).

---

## Issue Category 4: Admin Center Metric Visibility Issues

### Issue 4.1: Custom agent not appearing in Admin Center Agent Registry

**Symptom**: SDK-instrumented custom agent does not appear in M365 Admin Center > Agents > All Agents despite successful SDK initialization.

**Probable Causes**:
- The agent's Entra app registration is not linked to the Agent 365 registry
- The agent must be explicitly registered in addition to SDK instrumentation
- The SDK may not auto-register agents in all configurations during Preview

**Diagnostic Steps**:
1. Confirm the agent's Entra app registration exists and is active.
2. Check whether the agent needs to be explicitly registered in the Agent Registry. During Preview, some agent types require manual registration in addition to SDK instrumentation.
3. Review the Admin Center All Agents list with no filters applied to ensure filtering is not hiding the agent.

**Resolution**:
1. Manually register the agent via the Admin Center: Agents > All Agents > Add agent (if this option is available).
2. Alternatively, register the agent via the Microsoft Graph API for the Agent Registry endpoint.
3. Contact your FastTrack contact or open a Microsoft Support ticket if the agent is instrumented and authenticated correctly but still absent from the registry after 48 hours.

---

### Issue 4.2: Agent appears in registry but does not contribute to hero metrics

**Symptom**: Custom agent is visible in the All Agents list and shows as Active, but Total Sessions, Exception Rate, and Agent Runtime metrics remain unchanged after agent invocations.

**Probable Causes**:
- `ENABLE_A365_OBSERVABILITY_EXPORTER=true` is not set (see Issue 3.1)
- The agent platform is not yet supported for hero metric contribution (some platforms only contribute to registry count, not metrics)
- Frontier enrollment is not active

**Resolution**:
1. Verify `ENABLE_A365_OBSERVABILITY_EXPORTER=true` per Issue 3.1.
2. Confirm Frontier enrollment is active (hero metrics require Frontier).
3. Check the Agent 365 documentation for the list of supported platforms for metric contribution. If your platform is not listed, open a feedback item with Microsoft and document this as a known telemetry gap.

---

## Issue Category 5: Purview Audit Log Ingestion Issues

### Issue 5.1: Agent session records are not appearing in Purview Unified Audit Log

**Symptom**: Purview Audit search returns no records for agent sessions even after waiting 2+ hours.

**Probable Causes**:
- Purview audit logging is not enabled for the tenant
- The AgentSignIn or AgentSession record types are not yet available for this tenant region
- The Purview search parameters are incorrect

**Diagnostic Steps**:
1. Confirm audit logging is enabled: Purview compliance portal > Audit > If you see "Start recording user and admin activity," audit logging is disabled. Enable it.
2. Broaden the Purview search: remove the record type filter and search all activities for the agent's service principal name. This helps isolate whether the issue is record type filtering or actual absence of records.
3. Confirm the search date range includes the time of the test agent invocation with sufficient buffer (at least 2 hours on each side).

**Resolution**:
1. Enable audit logging if disabled: Purview > Audit > Start recording. Note: audit log activation can take 30–60 minutes.
2. If the `AgentSignIn` record type does not appear in the Purview record type filter, it is not yet GA in your tenant region. Document this as a known Preview limitation. As an interim measure, search for the agent's service principal in the broader audit log without a record type filter.
3. If the broader search also returns no results: the telemetry chain is broken upstream. Return to Issue 3.1 (export service connectivity).

---

### Issue 5.2: Purview audit search returns records but they do not contain agent session detail

**Symptom**: Purview audit search returns records associated with the agent service principal, but the records contain minimal information (no session ID, no tool call details, no exception data).

**Probable Causes**:
- Records are standard Entra sign-in events, not Agent 365 telemetry records
- SDK version is producing minimal telemetry (possible in early Preview versions)

**Resolution**:
1. Examine the RecordType field of the returned records. Standard Entra sign-in events have record type `AzureActiveDirectoryServicePrincipalSignIn`, which will not contain agent session detail. This is expected for sign-in events; look for distinct `AgentSession` or `AgentToolCall` record types for telemetry detail.
2. If only sign-in records appear and no session records are found, the telemetry export may be functioning for authentication but not for session activity. Verify SDK version and export configuration.
3. Upgrade to the latest available Preview SDK version, as earlier versions may produce limited telemetry.

---

## Issue Category 6: Microsoft Defender Integration Issues

### Issue 6.1: No Defender alert generated for test agent exception

**Symptom**: A test exception was triggered in the agent, but no corresponding alert appears in Microsoft Defender within 4 hours.

**Probable Causes**:
- Defender is not configured to alert on agent exception anomalies
- The exception severity was below Defender's alert threshold
- Defender does not yet have native Agent 365 anomaly detection rules during Preview

**Resolution**:
1. Check Microsoft Defender > Advanced hunting using the KQL queries in Playbook 3.14-C, Test 4. If the event appears in advanced hunting tables but no alert was generated, the issue is alert rule configuration, not telemetry ingestion.
2. Create a custom detection rule in Defender: Settings > Advanced hunting > Custom detection rules > Create rule. Build a rule that triggers on agent exception events from the CloudAppEvents or equivalent table.
3. During Preview, native Defender alerting for Agent 365 exceptions may not yet be available for all exception types. Document this as a known Preview limitation and rely on Log Analytics alert rules as the interim exception detection mechanism.

---

### Issue 6.2: Defender alerts generated but contain no agent attribution

**Symptom**: Defender generates alerts for agent-related activity but the alert details do not identify the specific agent, session ID, or the triggering action.

**Resolution**:
1. This is consistent with Preview-period alert enrichment limitations. The alert will gain richer agent-specific context as the Agent 365 Defender integration matures toward GA.
2. Use the alert timestamp and the `CorrelationId` or `SessionId` fields (if present) to cross-reference the Purview audit log or Log Analytics for complete context.
3. Establish a correlation procedure in your incident response runbook: when a Defender alert is identified as agent-related, the security analyst should immediately query the Purview audit log and Log Analytics using the alert timestamp as the search window.

---

## Issue Category 7: Entra Sign-In Log Attribute Issues

### Issue 7.1: "Is Agent = Yes" filter not available in Entra sign-in logs

**Symptom**: The "Is Agent = Yes" filter option described in Control 3.14 is not visible in the Entra admin center service principal sign-in logs UI.

**Probable Cause**: This filter is in Preview and may not yet be available in all tenant regions or for all Entra license tiers.

**Resolution**:
1. Check the Entra admin center preview features: Settings > Preview features. Confirm whether agent-specific sign-in features are listed and can be enabled.
2. As an interim measure, use the service principal name or application ID filter to isolate agent authentication events manually.
3. For Log Analytics-based filtering, use the KQL `where` clause to filter on `ServicePrincipalName` or `AppDisplayName` containing your agent name.
4. Monitor Microsoft 365 Message Center for announcements about the "Is Agent" filter GA date.

---

### Issue 7.2: MicrosoftServicePrincipalSignInLogs diagnostic setting returns error on creation

**Symptom**: When creating the `MicrosoftServicePrincipalSignInLogs` diagnostic setting in Entra, an error is returned indicating the log category is not valid.

**Probable Causes**:
- The exact log category name has changed from what is documented (common during Preview)
- A diagnostic setting for this category already exists and a duplicate is being created

**Diagnostic Steps**:
1. Navigate to Entra Admin Center > Monitoring & health > Diagnostic settings. Review existing settings.
2. If a setting already exists: edit it to add `MicrosoftServicePrincipalSignInLogs` rather than creating a new setting.
3. Check current Microsoft Learn documentation for the exact log category name as of the current month.

**Resolution**:
1. Use the Entra diagnostic settings UI (Playbook 3.14-A, Part 2) rather than PowerShell to get a current list of available log categories — the UI will only show log categories valid for your tenant.
2. If the category is truly not available: the feature has not yet rolled out to your tenant region. Document this as a known Preview limitation and plan to enable it when the feature becomes available.

---

## Issue Category 8: Regulatory Compliance Issues

### Issue 8.1: Immutability policy in "Unlocked" state — failed Zone 3 audit

**Symptom**: Internal Audit or an external examiner identifies that the Azure Blob Storage immutability policy for agent log storage is in the "Unlocked" (not "Locked") state, failing the WORM storage requirement for Zone 3.

**Regulatory Impact**: An Unlocked immutability policy does not satisfy SEC Rule 17a-4(f) requirements for non-rewriteable, non-erasable electronic records. This is a material compliance finding.

**Immediate Actions**:
1. **Do not delete the existing container or storage account** — doing so would destroy any records already stored there.
2. Immediately escalate to CCO, Legal, and CISO.
3. Determine whether any records in the storage container have been modified or deleted since the container was created. (Azure blob versioning or change feed can help confirm this.)

**Resolution**:
1. Lock the immutability policy immediately after CCO and Legal review confirms the 6-year retention period is correct:
   ```powershell
   $Policy = Get-AzStorageContainerImmutabilityPolicy `
       -ResourceGroupName $rg -StorageAccountName $sa -ContainerName $container
   Lock-AzStorageContainerImmutabilityPolicy `
       -ResourceGroupName $rg -StorageAccountName $sa `
       -ContainerName $container -Etag $Policy.Etag
   ```
2. Document the locking action with the date, approver, and reason for the prior gap.
3. Determine whether any records that should have been in WORM storage during the unlocked period need to be re-exported and placed under the now-locked policy.
4. Include this finding in the firm's compliance deficiency log and report to regulators if the gap is material under applicable FINRA/SEC rules.

---

### Issue 8.2: agentSignIn log retention period set to less than 6 years

**Symptom**: Purview audit retention policy review reveals the retention period for agent-related records is less than 6 years (e.g., 1 year default for E3 licenses).

**Regulatory Impact**: A retention period shorter than FINRA Rule 4511's 6-year requirement is a recordkeeping compliance deficiency.

**Resolution**:
1. Create a new Purview audit retention policy as described in Playbook 3.14-A, Part 3, with a duration of at least 2,190 days.
2. Set a higher priority than the existing default policy.
3. Note: Purview retention policies are prospective. Records that aged out under the previous shorter policy before the new policy was applied cannot be recovered. Document the gap period for CCO review.
4. Escalate to CCO to assess whether the retention gap requires FINRA self-reporting under applicable rules.

---

## Escalation Matrix

| Severity | Issue Type | First Contact | Second Contact | Response Target |
|---|---|---|---|---|
| P1 — Critical | WORM storage unlocked; retention policy below regulatory minimum | CCO + Legal + CISO immediately | Microsoft Support (if platform issue) | Immediate |
| P1 — Critical | Purview audit logging completely disabled; no agent telemetry records exist | CCO + CISO + IT Operations | Microsoft Support | Within 1 hour |
| P2 — High | SDK not exporting telemetry; Admin Center shows no custom agent data | IT Engineering Lead + CISO | FastTrack / Microsoft Support | Within 4 hours |
| P3 — Medium | Purview records found but missing expected detail; Defender not generating alerts | IT Engineering + Compliance Analyst | Microsoft Support | Within 1 business day |
| P4 — Low | Preview features not available in tenant region; minor attribute gaps | IT Governance Lead | Microsoft Tech Community | Within 1 week |
| Compliance | Audit finding — review log gaps, retention deficiencies | CCO | Legal / External Counsel | Per firm incident response policy |

---

## Useful Resources for SDK Troubleshooting

- **Agent 365 SDK Repository**: Check the official Microsoft GitHub repository for SDK release notes, known issues, and breaking changes. Search for `microsoft/agents-a365-observability` or the equivalent repository name.
- **OpenTelemetry Troubleshooting**: `https://opentelemetry.io/docs/concepts/sdk-configuration/` — since the SDK is OTel-based, standard OTel troubleshooting approaches apply.
- **Azure Identity Troubleshooting**: `https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/troubleshooting` — for DefaultAzureCredential and token acquisition issues.
- **Microsoft Graph Explorer**: `https://developer.microsoft.com/en-us/graph/graph-explorer` — test Graph API calls interactively before embedding in automation scripts.
- **M365 Message Center**: M365 Admin Center > Health > Message center — authoritative source for known Preview issues and upcoming changes.
- **FastTrack Support**: Contact your Microsoft FastTrack Success Architect for Preview-specific issues that are blocking implementation.

---

[Back to Control 3.14](../../../controls/pillar-3-reporting/3.14-agent-365-observability-sdk.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell and SDK Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)

*Updated: March 2026 | Version: v1.3*
