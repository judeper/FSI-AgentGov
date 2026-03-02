# Portal Walkthrough: Control 1.24 - Defender AI Security Posture Management (AI-SPM)

**Last Updated:** January 2026
**Portal:** Microsoft Defender for Cloud (Azure Portal)
**Estimated Time:** 2-3 hours

## Prerequisites

- [ ] Azure subscription with Defender for Cloud enabled
- [ ] Security Admin or Subscription Owner role
- [ ] AI workloads deployed (Azure AI Foundry, Azure OpenAI, or Copilot Studio with Azure integration)

---

## Step-by-Step Configuration

### Step 1: Enable Defender for Cloud

1. Open [Azure Portal](https://portal.azure.com)
2. Navigate to **Microsoft Defender for Cloud**
3. Select **Environment settings** from the left menu
4. Select your subscription
5. Ensure **Defender CSPM** plan is enabled (required for AI-SPM)

### Step 2: Enable AI Security Posture Management

1. In Defender for Cloud, navigate to **Environment settings**
2. Select your subscription
3. Under **Defender CSPM**, click **Settings**
4. Enable **AI security posture management** toggle
5. Click **Save**

### Step 3: Configure AI Workload Discovery

1. Navigate to **Inventory** in Defender for Cloud
2. Filter by resource type: **AI/ML services**
3. Verify AI resources are discovered:
   - Azure OpenAI Service
   - Azure AI Services (Cognitive Services)
   - Azure Machine Learning workspaces
   - Azure AI Foundry projects

### Step 4: Review Attack Paths

1. Navigate to **Attack path analysis** in Defender for Cloud
2. Filter by **AI workloads** or search for "AI"
3. Review attack paths targeting:
   - AI model endpoints
   - Data stores used by AI services
   - Service principals with AI permissions
4. Prioritize remediation based on risk score

### Step 5: Review AI Security Recommendations

1. Navigate to **Recommendations** in Defender for Cloud
2. Filter by:
   - Resource type: AI/ML services
   - Category: Identity, Data, Network
3. Review recommendations such as:
   - Enable managed identity for AI services
   - Restrict network access to AI endpoints
   - Enable diagnostic logging for AI services
   - Rotate API keys regularly

### Step 6: Configure Multi-Cloud Connectors (Optional)

If you have AI workloads in AWS or GCP:

1. Navigate to **Environment settings**
2. Click **Add environment** > **Amazon Web Services** or **Google Cloud Platform**
3. Follow the connector wizard
4. Enable AI workload discovery for:
   - AWS: Amazon Bedrock, SageMaker
   - GCP: Vertex AI, AI Platform

### Step 7: Set Up Alerting

1. Navigate to **Security alerts** > **Alert rules**
2. Create custom rules for AI-specific scenarios:
   - Unusual AI API access patterns
   - High-volume prompt requests
   - AI model configuration changes
3. Configure notification to SOC team

---

## Configuration by Governance Level

| Setting | Baseline (Zone 1) | Recommended (Zone 2) | Regulated (Zone 3) |
|---------|-------------------|----------------------|-------------------|
| **AI-SPM Enabled** | Yes | Yes | Yes |
| **Discovery Frequency** | Daily | Daily | Continuous |
| **Attack Path Review** | Monthly | Weekly | Daily |
| **Recommendation Review** | Monthly | Weekly | Daily |
| **Critical Remediation SLA** | 30 days | 14 days | 72 hours |
| **Multi-cloud Connectors** | Optional | If applicable | Required if applicable |
| **Sentinel Integration** | Optional | Recommended | Required |

---

## Validation

After completing these steps, verify:

- [ ] AI-SPM is enabled in Defender for Cloud
- [ ] AI workloads appear in inventory
- [ ] Attack paths targeting AI are visible
- [ ] Security recommendations are generated
- [ ] Alerting is configured for AI security events

---

[Back to Control 1.24](../../../controls/pillar-1-security/1.24-defender-ai-security-posture-management.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
