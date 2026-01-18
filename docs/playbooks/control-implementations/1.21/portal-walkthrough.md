# Portal Walkthrough: Control 1.21 - Adversarial Input Logging

**Last Updated:** January 2026
**Portal:** Microsoft Purview, Microsoft Sentinel, Defender for Cloud Apps
**Estimated Time:** 3-4 hours

## Prerequisites

- [ ] Purview Audit enabled (Control 1.7)
- [ ] Microsoft Sentinel workspace (optional but recommended)
- [ ] Security Administrator role

---

## Step-by-Step Configuration

### Step 1: Enable Copilot Interaction Logging

1. Verify Purview Audit is enabled (Control 1.7)
2. Ensure Copilot activities are in scope
3. Verify retention meets requirements (6+ years)

### Step 2: Configure Defender for Cloud Apps AI Monitoring

1. Open [Microsoft Defender Portal](https://security.microsoft.com)
2. Navigate to **Cloud apps** > **Policies**
3. Create policy for AI agent monitoring:
   - Type: Activity policy
   - Filter: App = Copilot Studio
   - Condition: High-risk keywords detected

### Step 3: Create Sentinel Analytics Rules

1. Open [Azure Sentinel](https://portal.azure.com)
2. Navigate to **Analytics** > **Create rule**
3. Configure adversarial pattern detection:

```kql
// Example KQL for prompt injection detection
AuditLogs
| where ActivityDisplayName contains "Copilot"
| where TargetResources contains "ignore previous"
   or TargetResources contains "system prompt"
   or TargetResources contains "DAN mode"
   or TargetResources contains "jailbreak"
| project TimeGenerated, UserPrincipalName, ActivityDisplayName, TargetResources
```

### Step 4: Configure Encoding Detection

Create rule for Base64/obfuscation detection:

```kql
// Base64 pattern detection
AuditLogs
| where TargetResources matches regex @"^[A-Za-z0-9+/]{50,}={0,2}$"
| project TimeGenerated, UserPrincipalName, TargetResources
```

### Step 5: Set Zone-Based Responses

| Zone | Detection | Response |
|------|-----------|----------|
| Zone 1 | Log only | Weekly review |
| Zone 2 | Log + Alert | SOC notification |
| Zone 3 | Log + Alert + Block | Immediate response |

---

## Configuration by Governance Level

| Setting | Baseline (Tier 1) | Recommended (Tier 2) | Regulated (Tier 3) |
|---------|-------------------|----------------------|-------------------|
| **Detection** | Basic patterns | Standard + encoding | Comprehensive |
| **Response** | Log only | Alert | Block + Alert |
| **Review** | Monthly | Weekly | Real-time |
| **Retention** | 1 year | 6 years | 6+ years |

---

## Validation

After completing these steps, verify:

- [ ] Audit captures Copilot interactions
- [ ] Sentinel rule triggers on test adversarial input
- [ ] Encoding detection identifies Base64 patterns
- [ ] Zone-based response works correctly

---

[Back to Control 1.21](../../../controls/pillar-1-security/1.21-adversarial-input-logging.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
