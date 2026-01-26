# Control 1.12: Insider Risk Detection and Response - Troubleshooting

> This playbook provides troubleshooting guidance for [Control 1.12](../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md).

---

## Common Issues

### Issue: No Alerts Being Generated

**Symptoms:** Policy active but no alerts

**Solutions:**

1. Verify policy is in "Production" mode (not test)
2. Check user scope includes target users
3. Review indicator thresholds (may be too high)
4. Verify data connectors are functioning
5. Wait 24-48 hours for initial data collection

---

### Issue: Too Many False Positives

**Symptoms:** High volume of non-risky alerts

**Solutions:**

1. Adjust threshold settings to higher values
2. Refine priority content selection
3. Use priority user groups to focus
4. Add exclusions for known legitimate activities
5. Review and tune indicator weights

---

### Issue: HR Connector Not Working

**Symptoms:** Departing user policy not triggering

**Solutions:**

1. Verify HR connector configuration
2. Check field mappings are correct
3. Validate test user has resignation date
4. Review connector logs for errors
5. Ensure Azure AD integration is active

---

### Issue: Cannot See User Activities

**Symptoms:** Alert shows no activity details

**Solutions:**

1. Verify audit logging is enabled
2. Check user isn't in privacy exclusion
3. Confirm reviewer has proper role
4. Review privacy settings in config
5. Enable content preview if needed

---

### Issue: Alerts Not Escalating

**Symptoms:** High-severity alerts not creating cases

**Solutions:**

1. Verify escalation rules are configured
2. Check investigator assignments
3. Review alert severity mapping
4. Confirm notification settings
5. Check for workflow bottlenecks

---

### Issue: Analytics Not Showing Data

**Symptoms:** Analytics dashboard empty after 48 hours

**Solutions:**

1. Verify analytics is enabled
2. Check sufficient data volume exists
3. Confirm policies are active
4. Review data connector status
5. Contact Microsoft support if persists

---

### Issue: Priority User Group Not Applied

**Symptoms:** Priority users not receiving enhanced monitoring

**Solutions:**

1. Verify user is member of priority group
2. Check policy includes priority user group
3. Confirm group synchronization complete
4. Review group membership sources
5. Test with new user added to group

---

## Escalation Path

If issues persist:

1. **First tier**: Insider Risk Admin - policy configuration
2. **Second tier**: HR - data connector coordination
3. **Third tier**: Legal - investigation procedures
4. **Fourth tier**: Microsoft Support - platform issues

---

*Updated: January 2026 | Version: v1.2*
