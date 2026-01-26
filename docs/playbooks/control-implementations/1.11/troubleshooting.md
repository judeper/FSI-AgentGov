# Control 1.11: Conditional Access and Phishing-Resistant MFA - Troubleshooting

> This playbook provides troubleshooting guidance for [Control 1.11](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md).

---

## Common Issues

### Issue: Users Blocked by CA Policy Unexpectedly

**Symptoms:** Legitimate users cannot access Power Platform or Copilot Studio

**Solutions:**

1. Open failed sign-in > Conditional Access tab > capture failure reason
2. Use What if with same user/app/device/location to reproduce
3. Validate group targeting and exclusions
4. Confirm client app type and device state match policy
5. Verify Named Locations and IP range updates

---

### Issue: Break-Glass Account Blocked or Challenged

**Symptoms:** Emergency access account cannot sign in during incident

**Solutions:**

1. Confirm account is excluded from all CA policies
2. Check Sign-in logs for CA details
3. Validate account not subject to auth method restrictions
4. Ensure account not blocked by other controls
5. After incident: rotate credentials and document root cause
6. Run What if to confirm exclusions still apply

---

### Issue: Phishing-Resistant MFA Not Working

**Symptoms:** Users cannot complete phishing-resistant MFA with FIDO2 keys

**Solutions:**

1. Verify FIDO2 method is enabled in Authentication methods
2. Check user has registered a FIDO2 key
3. Confirm browser supports WebAuthn
4. Verify authentication strength policy includes FIDO2
5. Test with different FIDO2 key to rule out hardware
6. Review sign-in log Authentication Details

---

### Issue: Authentication Strength Not Enforced

**Symptoms:** Users authenticate with weaker methods than intended

**Solutions:**

1. Validate CA policy grant control is set to correct Authentication Strength
2. Ensure user is in-scope (group, app, exclusions)
3. Review sign-in Applied Conditional Access Policies
4. Check user's registered methods vs strength policy
5. Move from Report-only to On in staged rollout
6. Verify Authentication Strength Id matches intended policy

---

### Issue: Agent ID Not Showing Agents

**Symptoms:** Agent ID dashboard shows zero agents despite active agents

**Solutions:**

1. Verify tenant is enrolled in Agent ID preview
2. Check agents are using service principals
3. Confirm agents have made recent auth attempts
4. Wait for data synchronization (24-48 hours)
5. Verify permissions to view Agent ID

---

### Issue: Report-Only Policy Not Logging

**Symptoms:** CA policy in report-only mode not showing in logs

**Solutions:**

1. Verify policy is in "enabledForReportingButNotEnforced" state
2. Check users are within policy scope
3. Review Sign-in logs > Applied Conditional Access Policies
4. Confirm policy conditions are being met
5. Wait for log ingestion (up to 2 hours)

---

### Issue: CA Policy Not Applying to Agent Creators

**Symptoms:** Users can create agents without meeting CA requirements

**Solutions:**

1. Verify policy targets correct applications (Power Platform apps)
2. Check if user is in exclusion group
3. Confirm policy state is Enabled (not report-only)
4. Review if trusted location is bypassing policy
5. Check for conflicting policies
6. Validate sign-in event shows target app matches policy

---

### Issue: Named Location Not Recognized

**Symptoms:** Users at corporate office still challenged as untrusted

**Solutions:**

1. Verify IP ranges are correctly configured
2. Check for IPv6 addresses if IPv6 enabled
3. Confirm location is marked as trusted
4. Review if user is behind proxy/VPN
5. Test from known IP address

---

## Escalation Path

If issues persist:

1. **First tier**: Identity Administrator - CA and MFA configuration
2. **Second tier**: Entra Security Admin - authentication policies
3. **Third tier**: Entra Administrator - platform-level issues
4. **Fourth tier**: Microsoft Support - service issues

---

*Updated: January 2026 | Version: v1.2*
