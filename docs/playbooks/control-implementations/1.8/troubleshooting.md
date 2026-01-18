# Control 1.8: Runtime Protection and External Threat Detection - Troubleshooting

> This playbook provides troubleshooting guidance for [Control 1.8](../../../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md).

---

## Common Issues

### Issue: Runtime Protection Not Blocking Threats

**Symptoms:** Malicious prompts not being blocked

**Solutions:**

1. Verify Managed Environment is enabled
2. Check runtime protection settings are active
3. Review sensitivity threshold (may need adjustment)
4. Ensure agent security settings are configured
5. Check for policy conflicts

---

### Issue: Too Many False Positives

**Symptoms:** Legitimate queries being blocked

**Solutions:**

1. Review blocking patterns
2. Adjust sensitivity from High to Medium
3. Add exclusions for common legitimate patterns
4. Tune content moderation thresholds
5. Review and whitelist specific scenarios

---

### Issue: Alerts Not Being Generated

**Symptoms:** Security events not triggering alerts

**Solutions:**

1. Verify alert policy is enabled
2. Check activity matches alert conditions
3. Confirm notification recipients are valid
4. Review alert threshold settings
5. Check mailflow for alert delivery

---

### Issue: SIEM Not Receiving Events

**Symptoms:** Power Platform events missing in SIEM

**Solutions:**

1. Verify data export is configured
2. Check Event Hub connectivity
3. Confirm data connector is enabled in Sentinel
4. Review permissions for data streaming
5. Check for throttling or quota issues

---

### Issue: External Threat Detection Webhook Not Responding

**Symptoms:** Agent tool invocations timing out

**Solutions:**

1. Verify webhook endpoint is publicly accessible via HTTPS
2. Confirm endpoint responds within 1-second timeout
3. Check Entra app registration exists with correct Application ID
4. Verify Federated Identity Credential is configured correctly
5. Test endpoint manually using curl/Postman

---

### Issue: External Threat Detection Blocking Legitimate Tool Calls

**Symptoms:** Valid agent tool invocations being blocked

**Solutions:**

1. Review external provider's evaluation criteria
2. Check if specific tools are triggering false positives
3. Temporarily set default behavior to "Allow" to isolate issue
4. Work with provider to tune detection rules
5. Consider using Microsoft Defender integration

---

### Issue: Federated Identity Credential Authentication Failing

**Symptoms:** Webhook receives requests but authentication fails

**Solutions:**

1. Regenerate FIC subject identifier with correct base64 encoding
2. Verify tenant ID is correct in issuer URL and subject
3. Confirm webhook endpoint URL matches exactly
4. Check app registration has not been modified
5. Review Entra sign-in logs for error details

---

## Escalation Path

If issues persist:

1. **First tier**: Power Platform Administrator - verify configuration
2. **Second tier**: Security Operations - check alert/SIEM issues
3. **Third tier**: Microsoft Support - platform-level issues

---

*Updated: January 2026 | Version: v1.1*
