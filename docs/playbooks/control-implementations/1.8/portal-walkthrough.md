# Control 1.8: Runtime Protection and External Threat Detection - Portal Walkthrough

> This playbook provides portal configuration guidance for [Control 1.8](../../../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md).

---

## Prerequisites

- Managed Environments enabled (Control 2.1)
- Security operations team identified
- Incident response procedures documented
- Alert recipients and escalation paths defined
- Microsoft Defender for Cloud Apps license (for native Defender integration)
- Microsoft 365 App Connector configured in Defender portal (for native Defender integration)

---

## Step 1: Enable Managed Environments

**Portal Path:** Power Platform Admin Center > Environments > [Environment] > Enable Managed Environment

1. Navigate to [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
2. Select target environment
3. Click **Enable Managed Environment** (if not already enabled)
4. Confirm enablement
5. Wait for activation (may take up to 30 minutes)

---

## Step 2: Configure Agent Security Settings

**Portal Path:** Power Platform Admin Center > Environments > [Environment] > Settings > Features > Agent capabilities

1. Navigate to environment settings
2. Go to **Features** > **Agent capabilities**
3. Configure security settings:

| Setting | Recommended | Zone 3 |
|---------|-------------|--------|
| Allow AI-generated responses | On | On (with guardrails) |
| Moderation and safety | Enabled | Enabled - Strict |
| Block prompt injection attempts | Enabled | Enabled |
| Log AI interactions | Enabled | Enabled - Verbose |

4. Click **Save**

---

## Step 3: Enable Runtime Protection

**Portal Path:** Power Platform Admin Center > Policies > Agent security

1. Navigate to **Policies** > **Agent security**
2. Enable **Runtime protection**
3. Configure protection levels:

**Prompt Injection Detection:**
- Sensitivity: High (recommended for FSI)
- Action: Block and log
- Notify: Security team

**Jailbreak Prevention:**
- Detection mode: Active
- Action: Block and alert
- Log level: Detailed

**Content Safety:**
- Categories: All (hate, violence, self-harm, sexual)
- Threshold: Strict
- Action: Block and log

---

## Step 4: Configure Copilot Studio Security Settings

**Portal Path:** Copilot Studio > [Agent] > Settings > Security

For each agent:

1. Open agent in [Copilot Studio](https://copilotstudio.microsoft.com)
2. Navigate to **Settings** > **Security**
3. Configure:

| Setting | Zone 1 | Zone 2 | Zone 3 |
|---------|--------|--------|--------|
| Authentication | Optional | Required | Required + MFA |
| Secure input | Off | On | On |
| Secure output | Off | On | On |
| Log conversations | Optional | Required | Required |

4. Under **Moderation**: Enable content moderation

---

## Step 5: Enable Native Microsoft Defender Integration (Recommended)

!!! success "Recommended for FSI Organizations"
    Native Microsoft Defender integration provides AI agent inventory, activity logging, and real-time protection through Defender for Cloud Apps. This is the recommended approach for financial services organizations with Microsoft 365 E5 licensing.

### Prerequisites for Native Defender Integration

| Requirement | Details |
|-------------|---------|
| **Licensing** | Microsoft Defender for Cloud Apps (included in Microsoft 365 E5) |
| **Roles** | Power Platform Admin + Entra Security Admin (Defender XDR access) |
| **Connector** | Microsoft 365 App Connector must be configured in Defender portal |

### Step 5a: Configure Microsoft Defender Portal

**Portal Path:** Microsoft Defender Portal > Settings > Cloud Apps > Connected Apps > Copilot Studio AI Agents

1. Navigate to [Microsoft Defender Portal](https://security.microsoft.com)
2. Go to **Settings** > **Cloud Apps**
3. Select **Connected apps** > **App connectors**
4. Verify **Microsoft 365** connector is connected and healthy
5. Navigate to **Settings** > **Cloud Apps** > **Copilot Studio AI Agents**
6. Turn **On** the **Copilot Studio AI Agents** feature

!!! warning "Microsoft 365 App Connector Required"
    The Microsoft 365 App Connector must be configured and connected before enabling Copilot Studio AI Agents. This connector enables activity logging and is required for full functionality.

### Step 5b: Enable in Power Platform Admin Center

**Portal Path:** Power Platform Admin Center > Security > Threat detection > Microsoft Defender - Copilot Studio AI Agents

1. Navigate to [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
2. Go to **Security** in the left navigation
3. Select **Threat detection**
4. Click **Microsoft Defender - Copilot Studio AI Agents**
5. Toggle **Enable Microsoft Defender - Copilot Studio AI Agents** to **On**
6. Click **Manage** to configure environment-specific settings (optional)

### Step 5c: Verify Integration

After enabling:

| Verification | Timeline | How to Verify |
|--------------|----------|---------------|
| Initial connection | Up to 30 minutes | Check PPAC shows "Connected" status |
| AI agent inventory | 2-24 hours | View agent list in Defender portal |
| Activity logging | Near real-time | Check Defender CloudAppEvents for agent activities |
| Real-time protection | Immediate | Test blocked action generates Defender alert |

### Step 5d: Configure Environment Scope (Optional)

By default, native Defender integration applies to all environments. To configure specific environments:

1. In PPAC, click **Manage** next to the Defender toggle
2. Select specific environments to protect
3. Click **Save**

**FSI Zone Recommendation:**

| Zone | Native Defender | Rationale |
|------|----------------|-----------|
| Zone 1 - Personal | Optional | Lower risk, reduced licensing cost |
| Zone 2 - Team | **Required** | Shared agents require security monitoring |
| Zone 3 - Enterprise | **Required** | Customer-facing, regulatory compliance |

### Capabilities Enabled

When native Defender integration is enabled:

1. **AI Agents Inventory**
   - All Copilot Studio agents discovered and cataloged
   - Security posture visibility (misconfigurations, risky agents)
   - Agent data available in Defender XDR advanced hunting

2. **AI Agents Activity Logging**
   - Agent runtime invocations logged to Microsoft Purview
   - Tool calls, user prompts, and agent actions captured
   - Forensic investigation and compliance auditing enabled

3. **Real-Time Protection**
   - Suspicious tool invocations blocked before execution
   - UPIA/XPIA detection (prompt injection attacks)
   - Defender XDR alerts/incidents for blocked actions

### Post-Configuration Verification

After completing Steps 5a and 5b, verify the integration is working:

1. Return to Microsoft Defender Portal > Cloud Apps > AI Agent Inventory
2. Verify agents are appearing in inventory (may take up to 24 hours)
3. Navigate to Advanced Hunting and query CloudAppEvents table for agent activity data
4. Verify real-time protection is active by checking for policy enforcement events

!!! tip "FSI Compliance Guidance"
    For regulated environments, enable Defender integration for all Zone 2 and Zone 3 environments. Document the enablement date and configuration state for compliance evidence. Maintain a quarterly audit of AI agent inventory to ensure all production agents are monitored.

### Defender XDR Advanced Hunting Query

```kql
// Query agent activities in Defender
CloudAppEvents
| where Application == "Microsoft Copilot Studio"
| where ActionType == "AgentInteraction"
| extend AgentName = tostring(RawEventData.AgentName)
| extend ToolInvoked = tostring(RawEventData.ToolName)
| extend WasBlocked = tobool(RawEventData.Blocked)
| project Timestamp, AccountDisplayName, AgentName, ToolInvoked, WasBlocked
| order by Timestamp desc
```

---

## Step 6: Configure Additional Threat Detection (Third-Party Webhook)

!!! info "When to Use Additional Threat Detection"
    Use this section if you need to integrate with **third-party security providers** or **custom webhooks** in addition to (or instead of) native Microsoft Defender integration.

### Prerequisites for Additional Threat Detection

Before configuring Additional Threat Detection, ensure:

- Power Platform Admin role (or Entra Global Admin)
- Microsoft Entra application registered for webhook authentication
- Webhook endpoint URL from your security provider (third-party or custom)

### Step 6a: Create Entra App Registration

You have two options for creating the required app registration:

#### Option A: PowerShell Script (Recommended)

Microsoft provides a PowerShell script that automates app registration with Federated Identity Credentials (FIC):

```powershell
.\Create-CopilotWebhookApp.ps1 `
   -TenantId "your-tenant-id" `
   -Endpoint "https://your-defender-endpoint.azurewebsites.net/webhook" `
   -DisplayName "Copilot Security Integration" `
   -FICName "DefenderFIC"
```

See [PowerShell Setup](powershell-setup.md) for the complete script.

#### Option B: Manual Azure Portal Configuration

**Portal Path:** Microsoft Entra Admin Center > Applications > App registrations

1. Navigate to [Microsoft Entra Admin Center](https://entra.microsoft.com)
2. Go to **Applications** > **App registrations**
3. Click **+ New registration**
4. Configure:
   - **Name:** `CopilotStudio-ThreatDetection-Webhook`
   - **Supported account types:** Accounts in this organizational directory only (Single tenant)
5. Click **Register**
6. **Important:** Note the **Application (client) ID** - you will need this in Step 6c

### Step 6b: Configure Federated Identity Credentials

Federated Identity Credentials (FIC) enable secure authentication between Power Platform and your webhook without client secrets.

**Portal Path:** Microsoft Entra Admin Center > App registrations > [Your App] > Certificates & secrets

1. In the app registration, go to **Certificates & secrets**
2. Select the **Federated credentials** tab
3. Click **+ Add credential**
4. Select **Other issuer**
5. Configure the credential:

| Field | Value |
|-------|-------|
| **Issuer** | `https://login.microsoftonline.com/{your-tenant-id}/v2.0` |
| **Subject identifier** | `/eid1/c/pub/t/{base64-tenant-id}/a/m1WPnYRZpEaQKq1Cceg--g/{base64-endpoint}` |
| **Name** | `CopilotStudio-FIC` |
| **Audiences** | `api://AzureADTokenExchange` |

!!! warning "Subject Identifier Format"
    The subject identifier requires specific base64 encoding:

    - `{base64-tenant-id}` = Base64-encode your tenant GUID
    - `{base64-endpoint}` = Base64-encode your webhook endpoint URL

    See [PowerShell Setup](powershell-setup.md) for encoding examples.

6. Click **Add**

### Step 6c: Enable Additional Threat Detection in Power Platform

**Portal Path:** Power Platform Admin Center > Security > Threat detection > Additional threat detection

1. Navigate to [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
2. Go to **Security** in the left navigation
3. Select **Threat detection**
4. Click **Additional threat detection**
5. Select the environment you want to protect (e.g., "BMXRM" as shown in screenshot)
6. Click **Set up**

### Step 6d: Configure Threat Detection Settings

In the Additional threat detection configuration pane:

1. **Enable data sharing:**
   - Check: **Allow Copilot Studio to share data with a threat detection provider**
   - This consents to sharing agent interaction data with your security provider

2. **Azure Entra App ID:**
   - Enter the Application (client) ID from Step 6a
   - Example: `12345678-1234-1234-1234-123456789012`

3. **Endpoint link:**
   - Enter your security provider webhook URL
   - For Microsoft Defender: `https://your-defender-endpoint.azurewebsites.net/webhook`
   - For third-party providers: Obtain URL from provider documentation

4. **Error behavior:**

| Option | Description | FSI Recommendation |
|--------|-------------|-------------------|
| **Allow the agent to respond** | If provider is unavailable, agent continues | Zone 1 only |
| **Block the query** | If provider is unavailable, query is blocked | Zone 2/3 (Recommended for regulated environments) |

!!! danger "FSI Recommendation"
    For regulated financial services environments (Zone 2 and Zone 3), always select **Block the query**. This ensures a fail-closed security posture when the threat detection provider is unavailable.

5. Click **Save**

### Step 6e: Verify Configuration

After saving:

1. Wait up to 1 minute for App ID changes to propagate
2. Test with a sample agent interaction
3. Verify webhook receives the request
4. Check that response is returned within 1-second timeout

### Bulk Deployment via Environment Groups

For organizations with multiple environments, configure threat detection at the Environment Group level:

**Portal Path:** Power Platform Admin Center > Environments > Environment groups

1. Navigate to **Environments** > **Environment groups**
2. Select or create an Environment Group for your governance zone
3. Go to **Security settings**
4. Configure Additional threat detection settings
5. Settings will apply to all environments in the group

| Zone | Environment Group | Error Behavior |
|------|------------------|----------------|
| Zone 1 - Personal | `Personal-Productivity-EG` | Allow the agent to respond |
| Zone 2 - Team | `Team-Collaboration-EG` | Block the query |
| Zone 3 - Enterprise | `Enterprise-Managed-EG` | Block the query |

---

## Step 7: Configure Alert Policies

**Portal Path:** Microsoft Purview > Policies > Alert policies

### Alert 1: Prompt Injection Detected

1. Click **+ New alert policy**
2. Configure:
   - Name: `FSI-Agent-PromptInjection`
   - Severity: High
   - Activity: Custom (Power Platform audit log)
   - Condition: Operation = PromptInjectionBlocked
3. Notification: security-operations@contoso.com
4. Click **Save**

### Alert 2: Jailbreak Attempt

1. Create alert policy
2. Configure:
   - Name: `FSI-Agent-JailbreakAttempt`
   - Severity: Critical
   - Activity: Jailbreak detection event
3. Notification: SOC immediate alert
4. Click **Save**

---

## Step 8: Configure SIEM Integration

**Portal Path:** Power Platform Admin Center > Settings > Data export

1. Navigate to **Settings** > **Data export**
2. Enable activity log export to Event Hub
3. In Microsoft Sentinel:
   - Add **Power Platform** data connector
   - Enable Copilot Studio events and Security events

---

## Validation

After completing the configuration, verify:

1. [ ] Managed Environments enabled for target environments
2. [ ] Runtime protection settings configured with appropriate sensitivity levels
3. [ ] Prompt injection detection enabled and set to block
4. [ ] Content safety thresholds configured to strict
5. [ ] Alert policies created for prompt injection and jailbreak attempts
6. [ ] SIEM integration configured and receiving events
7. [ ] Test prompt injection attempt is blocked and logged
8. [ ] Additional threat detection configured for Zone 2/3 environments
9. [ ] Entra app registration created with Federated Identity Credentials
10. [ ] Webhook endpoint verified and responding within 1-second SLA (if using Additional Threat Detection)
11. [ ] Error behavior set to "Block the query" for regulated environments (if using Additional Threat Detection)
12. [ ] Native Microsoft Defender integration enabled for Zone 2/3 environments
13. [ ] AI agent inventory populated in Defender portal (within 24 hours)
14. [ ] Defender XDR alerts generated for blocked actions
15. [ ] Content moderation level set to High for all Zone 2/3 agents (Copilot Studio > Agent > Settings > Generative AI > Content moderation)
16. [ ] No agents have content moderation set below Medium without documented risk acceptance

**Expected Result:** Adversarial inputs are detected and blocked at runtime, security alerts fire within defined SLAs, all events flow to SIEM for correlation, and Defender threat detection evaluates tool invocations in real-time.

---

[Back to Control 1.8](../../../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: February 2026 | Version: v1.2*
