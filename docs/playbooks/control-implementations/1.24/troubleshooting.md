# Troubleshooting: Control 1.24 - Defender AI Security Posture Management

**Last Updated:** January 2026

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| AI-SPM not available | Defender CSPM not enabled | Enable Defender CSPM plan first |
| AI workloads not discovered | Discovery not running | Wait 24 hours after enablement; verify permissions |
| No attack paths shown | No vulnerabilities detected | Verify AI resources exist and are accessible |
| Multi-cloud not working | Connector misconfigured | Re-run connector wizard; check permissions |
| Recommendations missing | Feature still deploying | Wait 24-48 hours after initial enablement |

---

## Detailed Troubleshooting

### Issue: AI-SPM Toggle Not Visible

**Symptoms:** Cannot find AI security posture management option in Defender settings

**Resolution:**

1. Verify Defender CSPM (Cloud Posture) plan is enabled
2. Ensure subscription has Standard tier pricing
3. Check if your region supports AI-SPM (may be rolling out)
4. Verify you have Security Admin permissions

**Portal Path:**
```
Defender for Cloud > Environment settings > [Subscription] > Defender plans > Cloud Posture > Settings
```

---

### Issue: AI Workloads Not Appearing in Inventory

**Symptoms:** Azure AI services exist but don't appear in Defender inventory

**Resolution:**

1. Verify AI services are in monitored subscriptions
2. Check if resources are recently created (allow 4-24 hours for discovery)
3. Verify Resource Graph can see the resources:
   ```powershell
   Search-AzGraph -Query "Resources | where type =~ 'microsoft.cognitiveservices/accounts'"
   ```
4. Check for subscription-level exemptions in Defender

---

### Issue: Attack Paths Not Showing for AI Resources

**Symptoms:** Attack path analysis returns no results for AI workloads

**Resolution:**

1. Verify attack path analysis is enabled
2. Confirm AI resources have network exposure or identity access
3. Check if resources are protected by compensating controls (may reduce attack paths)
4. Wait 24-48 hours after AI-SPM enablement for initial analysis

---

### Issue: Multi-Cloud Connector Failing

**Symptoms:** AWS or GCP AI workloads not discovered

**Resolution:**

1. Verify connector status in Environment settings
2. Re-authenticate the cloud connector
3. For AWS:
   - Verify IAM role has correct permissions
   - Check CloudFormation stack status
4. For GCP:
   - Verify service account has required roles
   - Check organization/project scope

---

## Escalation Path

1. **Security Admin** - Defender configuration and permissions
2. **Cloud Security Architect** - Attack path interpretation
3. **Azure Support** - Platform issues with Defender for Cloud
4. **Microsoft Account Team** - Feature availability questions

---

## Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| Discovery delay | 4-24 hours for new resources | Use manual inventory for immediate needs |
| Regional availability | AI-SPM may not be in all regions | Check Azure status page |
| Multi-cloud gaps | Not all AWS/GCP AI services supported | Manual inventory for unsupported services |
| Attack path scope | May not cover all AI attack vectors | Supplement with threat modeling |

---

## Diagnostic Commands

### Check Defender Plan Status

```powershell
Get-AzSecurityPricing | Format-Table Name, PricingTier
```

### Check Resource Graph Connectivity

```powershell
Search-AzGraph -Query "Resources | take 1"
```

### List AI Resources Manually

```powershell
Get-AzResource | Where-Object {
    $_.ResourceType -match "cognitiveservices|machinelearning|openai"
} | Format-Table Name, ResourceType, ResourceGroupName
```

---

## Related Documentation

- [Defender for Cloud Troubleshooting](https://learn.microsoft.com/en-us/azure/defender-for-cloud/troubleshooting-guide)
- [Attack Path Analysis FAQ](https://learn.microsoft.com/en-us/azure/defender-for-cloud/attack-path-faq)
- [Multi-cloud Connector Setup](https://learn.microsoft.com/en-us/azure/defender-for-cloud/quickstart-onboard-aws)

---

[Back to Control 1.24](../../../controls/pillar-1-security/1.24-defender-ai-security-posture-management.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
