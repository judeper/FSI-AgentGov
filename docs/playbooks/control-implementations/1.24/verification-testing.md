# Verification & Testing: Control 1.24 - Defender AI Security Posture Management

**Last Updated:** January 2026

## Manual Verification Steps

### Test 1: Verify AI-SPM Enabled

1. Navigate to Defender for Cloud > Environment settings
2. Select subscription
3. Verify Defender CSPM is enabled with AI-SPM extension
4. **EXPECTED:** AI security posture management toggle is enabled

### Test 2: Verify AI Workload Discovery

1. Navigate to Defender for Cloud > Inventory
2. Filter by resource type: AI/ML services
3. **EXPECTED:** Azure AI services, ML workspaces, and OpenAI resources appear

### Test 3: Verify Attack Path Analysis

1. Navigate to Attack path analysis
2. Search for attack paths involving AI resources
3. **EXPECTED:** Attack paths targeting AI endpoints are identified

### Test 4: Verify Security Recommendations

1. Navigate to Recommendations
2. Filter for AI-related recommendations
3. **EXPECTED:** AI-specific security recommendations are generated

### Test 5: Verify Multi-Cloud Discovery (if applicable)

1. Navigate to Environment settings
2. Verify AWS/GCP connectors are configured
3. Check inventory includes non-Azure AI workloads
4. **EXPECTED:** AWS Bedrock or GCP Vertex AI resources appear (if configured)

---

## Test Cases

| Test ID | Scenario | Expected Result | Pass/Fail |
|---------|----------|-----------------|-----------|
| TC-1.24-01 | AI-SPM enabled | Toggle shows enabled | |
| TC-1.24-02 | AI workloads discovered | Resources in inventory | |
| TC-1.24-03 | Attack paths generated | AI attack paths visible | |
| TC-1.24-04 | Recommendations present | AI security recommendations | |
| TC-1.24-05 | Multi-cloud connector | Non-Azure AI discovered | |
| TC-1.24-06 | Risk factors assessed | Prompt injection risk shown | |

---

## Evidence Collection Checklist

- [ ] Screenshot: AI-SPM enabled in Defender for Cloud settings
- [ ] Screenshot: AI workload inventory
- [ ] Screenshot: Attack path analysis results
- [ ] Screenshot: AI security recommendations
- [ ] Export: AI workload inventory CSV
- [ ] Export: Attack paths targeting AI resources
- [ ] Export: Security recommendation status report

---

## Attestation Statement Template

```markdown
## Control 1.24 Attestation - Defender AI Security Posture Management

**Organization:** [Organization Name]
**Control Owner:** [Name/Role]
**Date:** [Date]

I attest that:

1. Defender for Cloud AI-SPM is enabled for all subscriptions hosting AI workloads
2. AI workload discovery is active and inventoried:
   - Azure AI Services: [Count]
   - Azure ML Workspaces: [Count]
   - Azure OpenAI: [Count]
3. Attack paths targeting AI resources are reviewed [weekly/daily] per zone requirements
4. Security recommendations for AI workloads are triaged and remediated per SLA:
   - Critical: [Count] (72-hour SLA for Zone 3)
   - High: [Count] (14-day SLA)
   - Medium: [Count] (30-day SLA)
5. Multi-cloud connectors are configured for [AWS/GCP] AI services: [Yes/No/N/A]

**AI Workloads Discovered:** [Count]
**Active Attack Paths:** [Count]
**Open Recommendations:** [Count]

**Signature:** _______________________
**Date:** _______________________
```

---

## Zone-Specific Testing Requirements

| Zone | Test Frequency | Attack Path Review | Recommendation Review |
|------|----------------|--------------------|-----------------------|
| Zone 1 | Monthly | Monthly | Monthly |
| Zone 2 | Weekly | Weekly | Weekly |
| Zone 3 | Daily | Daily | Daily |

---

## KQL Queries for Evidence

### Query AI Security Alerts (Sentinel)

```kql
SecurityAlert
| where TimeGenerated > ago(30d)
| where AlertType contains "AI" or AlertType contains "ML" or AlertType contains "cognitive"
| summarize count() by AlertType, AlertSeverity
| order by count_ desc
```

### Query Resource Graph for AI Inventory

```kql
// Run in Azure Resource Graph Explorer
Resources
| where type in~ (
    'microsoft.cognitiveservices/accounts',
    'microsoft.machinelearningservices/workspaces'
)
| summarize count() by type, location
```

---

[Back to Control 1.24](../../../controls/pillar-1-security/1.24-defender-ai-security-posture-management.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
