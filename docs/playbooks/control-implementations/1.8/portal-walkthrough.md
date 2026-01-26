# Control 1.8: Runtime Protection and External Threat Detection - Portal Walkthrough

> This playbook provides portal configuration guidance for [Control 1.8](../../../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md).

---

## Prerequisites

- Managed Environments enabled (Control 2.1)
- Security operations team identified
- Incident response procedures documented
- Alert recipients and escalation paths defined

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

| Setting | Recommended | Tier 3 |
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

| Setting | Tier 1 | Tier 2 | Tier 3 |
|---------|--------|--------|--------|
| Authentication | Optional | Required | Required + MFA |
| Secure input | Off | On | On |
| Secure output | Off | On | On |
| Log conversations | Optional | Required | Required |

4. Under **Moderation**: Enable content moderation

---

## Step 5: Configure External Threat Detection (Preview)

**Note:** This is a preview feature. Evaluate stability before production deployment.

### Step 5a: Create Entra App Registration

**Portal Path:** Microsoft Entra Admin Center > Applications > App registrations

1. Navigate to **Microsoft Entra Admin Center**
2. Go to **Applications** > **App registrations**
3. Click **+ New registration**
4. Configure:
   - Name: `CopilotStudio-ThreatDetection-Webhook`
   - Supported account types: Accounts in this organizational directory only
5. Click **Register**
6. Note the **Application (client) ID**

### Step 5b: Configure Federated Identity Credentials

1. In the app registration, go to **Certificates & secrets** > **Federated credentials**
2. Click **+ Add credential**
3. Select **Other issuer**
4. Configure per Microsoft documentation for Power Platform

### Step 5c: Enable in Power Platform

**Portal Path:** Power Platform Admin Center > Security > Threat detection > Additional threat detection

1. Navigate to **Security** > **Threat detection**
2. Select **Additional threat detection**
3. Configure:
   - Enable external threat detection: On
   - Enable data sharing: On
   - Application ID: [From Step 5a]
   - Endpoint URL: Your webhook URL
   - Default behavior on error: Block (recommended for FSI)
4. Click **Save**

---

## Step 6: Configure Alert Policies

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

## Step 7: Configure SIEM Integration

**Portal Path:** Power Platform Admin Center > Settings > Data export

1. Navigate to **Settings** > **Data export**
2. Enable activity log export to Event Hub
3. In Microsoft Sentinel:
   - Add **Power Platform** data connector
   - Enable Copilot Studio events and Security events

---

*Updated: January 2026 | Version: v1.2*
