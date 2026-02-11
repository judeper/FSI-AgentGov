# Control 1.8: Runtime Protection and External Threat Detection - Verification & Testing

> This playbook provides verification and testing guidance for [Control 1.8](../../../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md).

---

## Verification Steps

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Confirm Managed Environment | Environment shows as Managed |
| 2 | Test prompt injection detection | Blocked with log entry |
| 3 | Validate egress controls | Blocked connector/tool invocation logged |
| 4 | Verify alert configuration | FSI alerts created and enabled |
| 5 | Test content moderation | Appropriate moderation response |
| 6 | Validate SIEM integration (Zone 3) | Events streaming within SLA |
| 7 | Verify external threat detection | Webhook receives requests (if enabled) |
| 8 | Verify Additional Threat Detection config | App ID and endpoint configured correctly |
| 9 | Test Defender webhook connectivity | Webhook responds within 1 second |
| 10 | Validate error behavior | Correct action when provider unavailable |
| 11 | Verify native Defender integration | Toggle enabled in both portals |
| 12 | Validate AI agent inventory | Agents visible in Defender portal |
| 13 | Test Defender XDR alerting | Blocked action generates incident |

---

## Test Cases

### Test 1: Prompt Injection Detection

1. Submit test prompt with injection pattern (e.g., "ignore previous instructions")
2. **Expected:** Blocked with log entry
3. Verify event appears in audit log

### Test 2: Egress Controls

1. Attempt to invoke a blocked/high-risk connector from the agent
2. Attempt to reach a non-approved destination
3. **Expected:** Invocation blocked; audit log captured with policy reason

### Test 3: Content Moderation

1. Submit content that should be blocked (e.g., harmful content)
2. **Expected:** Appropriate moderation response
3. Verify moderation event logged

### Test 4: Alert Generation

1. Generate test security event (e.g., prompt injection attempt)
2. **Expected:** Alert generated and delivered to configured recipients
3. Verify alert appears in Purview

### Test 5: SIEM Integration

1. Generate test security event
2. **Expected:** Event appears in SIEM within SLA
3. Verify event correlation is working

### Test 6: Additional Threat Detection Configuration

1. Navigate to Power Platform Admin Center > Security > Threat detection > Additional threat detection
2. Select a Zone 2/3 environment
3. **Verify:** Data sharing is enabled
4. **Verify:** Azure Entra App ID is populated and valid
5. **Verify:** Endpoint link is populated with HTTPS URL
6. **Verify:** Error behavior is set to "Block the query" for regulated environments

### Test 7: Entra App Registration Verification

1. Navigate to Microsoft Entra Admin Center > App registrations
2. Search for the CopilotStudio-ThreatDetection app
3. **Verify:** App exists with correct display name
4. **Verify:** Sign-in audience is "Single tenant"
5. Navigate to Certificates & secrets > Federated credentials
6. **Verify:** FIC exists with correct issuer and subject identifier

### Test 8: Webhook Endpoint Connectivity

1. Use curl or Postman to test webhook endpoint:
   ```bash
   curl -X POST https://your-webhook-endpoint/api/evaluate \
     -H "Content-Type: application/json" \
     -d '{"test": true}'
   ```
2. **Expected:** Response within 1 second
3. **Expected:** HTTP 200 status code
4. **Verify:** Response format is valid (allow/block/warn)

### Test 9: End-to-End Defender Integration

1. Interact with a generative agent in a protected environment
2. Agent invokes a tool (e.g., retrieves data from SharePoint)
3. **Verify:** Webhook receives the tool invocation payload
4. **Verify:** Webhook returns evaluation within 1-second SLA
5. **Verify:** Agent action proceeds (if allowed) or is blocked (if denied)

### Test 10: Error Behavior Validation (Zone 2/3 Only)

1. Temporarily disable the webhook endpoint or simulate unavailability
2. Interact with a generative agent that invokes a tool
3. **Expected (if "Block the query"):** Agent query is blocked with error message
4. **Expected (if "Allow the agent to respond"):** Agent continues without threat evaluation
5. Re-enable webhook and verify normal operation resumes

### Test 11: Native Microsoft Defender Integration Configuration

1. Navigate to Microsoft Defender Portal > Settings > Cloud Apps > Copilot Studio AI Agents
2. **Verify:** Copilot Studio AI Agents toggle is **On**
3. **Verify:** Microsoft 365 App Connector is connected and healthy
4. Navigate to Power Platform Admin Center > Security > Threat detection
5. **Verify:** Microsoft Defender - Copilot Studio AI Agents toggle is **On**
6. **Verify:** Both portals show connected status

### Test 12: AI Agent Inventory Population

1. Wait 2-24 hours after enabling native Defender integration
2. Navigate to Microsoft Defender Portal > Identities > AI agents (or Cloud Apps > AI Agents)
3. **Verify:** Copilot Studio agents are listed in inventory
4. **Verify:** Agent metadata is populated (name, environment, owner)
5. **Verify:** Security posture indicators are displayed for each agent

### Test 13: Defender XDR Alert Generation

1. Trigger a blocked action (e.g., prompt injection in a protected agent)
2. Navigate to Microsoft Defender Portal > Incidents & alerts
3. **Verify:** Alert generated for blocked action
4. **Verify:** Alert contains agent name, user, and action details
5. **Verify:** Alert severity matches expected level (High for prompt injection)

### Test 14: Defender Advanced Hunting Query

1. Navigate to Microsoft Defender Portal > Hunting > Advanced hunting
2. Run the following query:
   ```kql
   CloudAppEvents
   | where Application == "Microsoft Copilot Studio"
   | where ActionType == "AgentInteraction"
   | take 10
   ```
3. **Verify:** Results return agent interaction events
4. **Verify:** Events include agent name, user, and action details

### Test 15: Activity Logging to Microsoft Purview

1. Interact with a protected generative agent
2. Navigate to Microsoft Purview > Audit log search
3. Search for Copilot Studio activities
4. **Verify:** Agent interaction events appear in audit log
5. **Verify:** Events include tool invocations and user prompts (metadata)

### Test 16: Defender CloudAppEvents for Agent Activity

1. Navigate to Microsoft Defender Portal > Hunting > Advanced hunting
2. Run the following query to verify Defender is capturing agent activity:
   ```kql
   CloudAppEvents
   | where Timestamp > ago(24h)
   | where Application == "Microsoft Copilot Studio"
   | extend ActionType = tostring(RawEventData.ActionType)
   | summarize count() by ActionType, bin(Timestamp, 1h)
   | order by Timestamp desc
   ```
3. **Verify:** Results show agent interaction events from the past 24 hours
4. **Verify:** Activity types include tool invocations, user prompts, and agent responses
5. **Verify:** Event volume matches expected agent usage patterns

### Test 17: DSPM Activity Explorer Integration with Defender Events

1. Navigate to Microsoft Purview > DSPM for AI > Activity explorer
2. Filter for Copilot Studio agent activities
3. **Verify:** Defender-sourced activity events appear in Activity Explorer
4. **Verify:** Events show security context (UPIA/XPIA detection flags if applicable)
5. **Verify:** Cross-portal consistency between Defender and Purview audit data

**Expected Result:** Defender activity logging integrates seamlessly with DSPM Activity Explorer for comprehensive compliance monitoring.

---

## Evidence Artifacts

- [ ] Screenshot: Managed environment confirmation
- [ ] Screenshot: Runtime protection settings
- [ ] Export: Alert policy configurations
- [ ] Log: Prompt injection detection test
- [ ] Export/screenshot: DLP policy and connector restrictions
- [ ] Log: Egress/tool blocking test
- [ ] Documentation: Incident response playbook
- [ ] SIEM: Power Platform connector status
- [ ] Screenshot: External threat detection configuration (if enabled)
- [ ] Documentation: Vendor risk assessment (if using third-party webhook)
- [ ] Screenshot: Additional threat detection settings in PPAC
- [ ] Screenshot: Entra app registration with FIC configured
- [ ] Log: Webhook endpoint connectivity test results
- [ ] Export: App registration details (AppId, ObjectId, FIC configuration)
- [ ] Documentation: Error behavior justification for each zone
- [ ] Screenshot: Native Defender integration toggle in Defender portal
- [ ] Screenshot: Native Defender integration toggle in PPAC
- [ ] Screenshot: AI agent inventory in Defender portal
- [ ] Screenshot: Defender XDR alert for blocked action
- [ ] Export: Advanced hunting query results
- [ ] Log: Purview audit log entries for agent interactions
- [ ] Export: CloudAppEvents query results for agent activity (Test 16)
- [ ] Screenshot: DSPM Activity Explorer showing Defender-sourced events (Test 17)

---

## Zone-Specific Testing

### Zone 1 (Personal Productivity)

- Runtime protection: Optional
- Prompt injection: Log only
- Response SLA: Best effort
- Native Defender: Optional
- Additional Threat Detection: Not required

### Zone 2 (Team Collaboration)

- Runtime protection: Required
- Prompt injection: Block and log
- Response SLA: 4 hours
- Native Defender: **Required**
- Additional Threat Detection: Optional (use if third-party provider needed)

### Zone 3 (Enterprise Managed)

- Runtime protection: Required - Maximum
- Prompt injection: Block, log, and investigate
- Response SLA: 15 minutes
- Incident playbook: Required
- Native Defender: **Required**
- Additional Threat Detection: Recommended for additional security layers
- AI agent inventory audit: Quarterly

---

## Confirmation Checklist

- [ ] Managed Environment is enabled
- [ ] Runtime protection settings are configured
- [ ] Prompt injection detection is active
- [ ] Content moderation is enabled
- [ ] Egress controls are in place
- [ ] Alert policies are created and enabled
- [ ] SIEM integration is functional (Zone 2-3)
- [ ] Incident response playbook is documented
- [ ] Evidence artifacts collected and stored
- [ ] Additional threat detection enabled for Zone 2/3 environments
- [ ] Entra app registration created with Federated Identity Credentials
- [ ] Webhook endpoint responds within 1-second SLA
- [ ] Error behavior set to "Block the query" for regulated environments
- [ ] Vendor risk assessment completed (if using third-party provider)
- [ ] Native Microsoft Defender integration enabled (Zone 2/3)
- [ ] AI agent inventory populated in Defender portal
- [ ] Defender XDR alerts verified for blocked actions
- [ ] M365 App Connector connected in Defender portal
- [ ] CloudAppEvents query returns agent activity data (Test 16)
- [ ] DSPM Activity Explorer shows Defender-sourced events (Test 17)

---

*Updated: February 2026 | Version: v1.2*
