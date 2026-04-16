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

### Issue: "Problem saving settings" in Additional Threat Detection

**Symptoms:** Error when saving Additional Threat Detection configuration in PPAC

**Solutions:**

1. Verify the Entra app registration exists and is not deleted
2. Confirm the Application ID format is correct (GUID format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
3. Check that Federated Identity Credential is properly configured
4. Verify the endpoint URL is HTTPS and publicly accessible
5. Ensure you have Power Platform Admin role
6. Wait 1 minute and retry (propagation delay)

---

### Issue: "Connection to protection provider failed"

**Symptoms:** Agent interactions fail with connection error to threat detection provider

**Solutions:**

1. Verify webhook endpoint is publicly accessible (not behind firewall/VPN)
2. Test endpoint connectivity with curl or Postman
3. Check endpoint SSL certificate is valid and not expired
4. Verify endpoint responds within 1-second timeout
5. Review Azure Function/API Gateway logs if hosting custom webhook
6. Check for rate limiting or throttling on the endpoint

---

### Issue: Agent Tool Invocations Timing Out

**Symptoms:** Agent interactions hang when invoking tools in protected environments

**Solutions:**

1. Verify webhook endpoint response time is under 1 second
2. Check for network latency between Power Platform and webhook
3. Optimize webhook code for faster response
4. Consider caching threat evaluation results for common patterns
5. Review webhook infrastructure scaling (Azure Function consumption plan may cold-start)
6. Temporarily set error behavior to "Allow" to isolate timeout issue

---

### Issue: Defender Not Receiving Tool Invocation Requests

**Symptoms:** No requests appearing in Defender/webhook logs

**Solutions:**

1. Verify Additional Threat Detection is enabled in PPAC for the environment
2. Confirm the agent is a generative orchestration agent (classic agents not supported)
3. Check the agent is published and users are interacting with it
4. Verify data sharing consent is enabled
5. Review Entra app registration sign-in logs for authentication failures
6. Ensure Environment Group settings are not overriding environment-level config

---

### Issue: App ID Changes Not Taking Effect

**Symptoms:** Updated App ID not recognized by Power Platform

**Solutions:**

1. Wait up to 1 minute for propagation (documented delay)
2. Clear browser cache and refresh PPAC
3. Sign out and sign back in to PPAC
4. Verify the new app registration is in the correct tenant
5. Check that old app registration is not being cached

---

### Issue: Base64 Encoding Errors in FIC Subject Identifier

**Symptoms:** FIC configuration fails with invalid subject error

**Solutions:**

1. Use PowerShell to generate correct base64 encoding:
   ```powershell
   $TenantIdBase64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($TenantId))
   $EndpointBase64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($WebhookEndpoint))
   ```
2. Ensure no trailing newlines or spaces in the encoded values
3. Verify the subject identifier format matches exactly:
   `/eid1/c/pub/t/{base64-tenant-id}/a/m1WPnYRZpEaQKq1Cceg--g/{base64-endpoint}`
4. Use the provided PowerShell script for automated encoding

---

### Issue: Error Behavior "Block" Causing Production Outages

**Symptoms:** Legitimate agent interactions blocked when Defender is temporarily unavailable

**Solutions:**

1. Review Defender/webhook service health and SLA
2. Implement high-availability for webhook endpoint (multiple regions, load balancing)
3. Configure alerting for webhook endpoint availability
4. For Zone 1 environments, consider switching to "Allow the agent to respond"
5. Implement circuit breaker pattern in webhook to fail fast
6. Document incident response procedures for threat detection provider outages

---

## Native Microsoft Defender Integration Issues

### Issue: Native Defender Toggle Not Available in PPAC

**Symptoms:** "Microsoft Defender - Copilot Studio AI Agents" option not visible in Security > Threat detection

**Solutions:**

1. Verify you have Microsoft Defender for Cloud Apps license (M365 E5)
2. Ensure you have Power Platform Admin role
3. Check if the feature is enabled in your tenant (may require tenant enablement)
4. Verify the Defender portal has Copilot Studio AI Agents feature enabled first
5. Wait 30 minutes after enabling in Defender portal before checking PPAC

---

### Issue: AI Agent Inventory Not Populating

**Symptoms:** No agents visible in Defender portal after enabling integration (24+ hours)

**Solutions:**

1. Verify native Defender integration is enabled in **both** portals:
   - Microsoft Defender Portal: Settings > Cloud Apps > Copilot Studio AI Agents = On
   - Power Platform Admin Center: Security > Threat detection > Microsoft Defender toggle = On
2. Confirm Microsoft 365 App Connector is connected in Defender portal
3. Ensure agents are **generative orchestration agents** (classic agents not supported)
4. Verify agents are published and have recent user interactions
5. Check Defender service health for any ongoing issues
6. Wait full 24-hour propagation period before escalating

---

### Issue: Microsoft 365 App Connector Not Connected

**Symptoms:** Defender shows M365 App Connector disconnected or unhealthy

**Solutions:**

1. Navigate to Defender Portal > Settings > Cloud Apps > App connectors
2. Locate **Microsoft 365** connector and check status
3. If disconnected, click **Reconnect** and follow authentication flow
4. Ensure service account has required permissions:
   - Entra Global Admin (for initial setup)
   - Or Entra Security Admin + Purview Compliance Admin
5. Verify OAuth consent has not been revoked in Entra ID
6. Check Entra audit logs for any app permission changes

---

### Issue: Defender XDR Alerts Not Generating for Blocked Actions

**Symptoms:** Agent tool invocations blocked but no alerts appear in Defender

**Solutions:**

1. Verify real-time protection is active (check agent interaction logs)
2. Confirm blocked action was actually blocked by Defender (not by DLP or other policy)
3. Check alert filters in Defender portal - ensure Copilot Studio alerts are not filtered out
4. Review alert policies - custom policies may override default alerting
5. Wait 15-30 minutes for alert propagation
6. Use Advanced Hunting to query CloudAppEvents for blocked actions:
   ```kql
   CloudAppEvents
   | where Application == "Microsoft Copilot Studio"
   | where ActionType contains "Blocked"
   | take 50
   ```

---

### Issue: Defender Portal Shows "Not Connected" Status

**Symptoms:** PPAC shows toggle enabled but Defender portal shows disconnected

**Solutions:**

1. Re-toggle the integration off and on in PPAC
2. Wait 30 minutes for synchronization
3. Verify both admin accounts (PPAC and Defender) are in the same tenant
4. Check for any Conditional Access policies blocking the integration
5. Review Defender service health status
6. Contact Microsoft Support if status remains inconsistent after 1 hour

---

### Issue: Licensing Errors When Enabling Defender Integration

**Symptoms:** Error message about insufficient licensing when enabling toggle

**Solutions:**

1. Verify Defender for Cloud Apps license is assigned to admin account
2. Check tenant has active M365 E5 or Defender for Cloud Apps standalone license
3. Ensure license is properly activated (may take 24 hours after purchase)
4. Verify license is assigned to users who will interact with protected agents
5. Review Microsoft 365 Admin Center > Billing > Licenses for license status

---

### Issue: Defender Integration Causing Agent Performance Degradation

**Symptoms:** Agent responses noticeably slower after enabling Defender integration

**Solutions:**

1. Defender inspection adds ~100-200ms latency per tool invocation (expected)
2. Check Defender service health for any performance issues
3. Review agent complexity - many tool invocations multiply latency impact
4. Consider if latency is acceptable for use case (Zone 3 may tolerate more latency for security)
5. Monitor CloudAppEvents for timeout or retry patterns
6. If latency exceeds 1 second consistently, open Microsoft Support case

---

## Escalation Path

If issues persist:

1. **First tier**: Power Platform Admin - verify configuration
2. **Second tier**: Security Operations - check alert/SIEM issues
3. **Third tier**: Entra Security Admin - app registration and FIC issues
4. **Fourth tier**: Microsoft Support - platform-level issues

For Additional Threat Detection (third-party webhook) issues:

| Issue Category | Escalation Path |
|---------------|-----------------|
| App registration/FIC | Entra Security Admin → Microsoft Identity Support |
| Webhook connectivity | Network Admin → Azure Support (if Azure-hosted) |
| PPAC configuration errors | Power Platform Admin → Microsoft Power Platform Support |

For Native Microsoft Defender Integration issues:

| Issue Category | Escalation Path |
|---------------|-----------------|
| Defender portal configuration | Entra Security Admin → Microsoft Defender Support |
| PPAC toggle issues | Power Platform Admin → Microsoft Power Platform Support |
| M365 App Connector | Entra Security Admin → Microsoft Defender Support |
| Agent inventory issues | Security Operations → Microsoft Defender Support |
| Licensing issues | Microsoft 365 Admin → Microsoft Licensing Support |
| Cross-portal sync issues | Both admins coordinate → Microsoft Support (joint ticket) |

---

## Related Playbooks

- [Portal Walkthrough](./portal-walkthrough.md) - Step-by-step portal configuration
- [PowerShell Setup](./powershell-setup.md) - Automation scripts
- [Verification & Testing](./verification-testing.md) - Test procedures

---

*Updated: February 2026 | Version: v1.3*
