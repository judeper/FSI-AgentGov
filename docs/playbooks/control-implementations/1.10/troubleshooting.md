# Control 1.10: Communication Compliance Monitoring - Troubleshooting

> This playbook provides troubleshooting guidance for [Control 1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md).

---

## Common Issues

### Issue: Policy Not Detecting Violations

**Symptoms:** Known violations not generating alerts

**Solutions:**

1. Verify policy is enabled
2. Check user scope includes target users
3. Verify location scope (Teams, email, etc.)
4. Review keyword/SIT configuration
5. Check classifier is enabled and trained
6. Validate message type is supported for monitoring
7. Verify audit logs show underlying activity

---

### Issue: Too Many False Positives

**Symptoms:** High volume of non-violation alerts

**Solutions:**

1. Tune keyword lists (add exclusions)
2. Adjust sensitivity thresholds
3. Review and refine classifiers
4. Add context conditions
5. Use sample-based review instead of 100%
6. Track tuning changes and compare volumes

---

### Issue: Reviewers Not Receiving Alerts

**Symptoms:** Alerts stuck in queue

**Solutions:**

1. Verify reviewer role assignments
2. Check email notifications configured
3. Verify reviewer mailbox is active
4. Review routing rules
5. Check for Teams notification issues
6. Confirm reviewer can access Purview UI

---

### Issue: Copilot Conversations Not Captured

**Symptoms:** Agent interactions not appearing

**Solutions:**

1. Verify Copilot location is selected in policy
2. Check licensing for Copilot capture
3. Review audit log for Copilot events
4. Verify agent is integrated with monitored channel
5. Validate interaction type is supported
6. Open Microsoft support ticket if needed

---

### Issue: Classifiers Not Working

**Symptoms:** AI classifiers not detecting expected content

**Solutions:**

1. Verify classifier is enabled in settings
2. Check classifier availability in your tenant
3. Review classifier requirements (training data)
4. Test with known content that should match
5. Allow time for classifier processing

---

### Issue: OCR Not Processing Images

**Symptoms:** Sensitive content in images not detected

**Solutions:**

1. Verify OCR is enabled in settings
2. Check image is in supported format
3. Verify image quality is sufficient
4. Check attachment is within size limits
5. Review OCR processing logs

---

### Issue: Alert Routing Not Working

**Symptoms:** Alerts not reaching correct reviewers

**Solutions:**

1. Verify priority user groups configured
2. Check alert routing rules
3. Confirm notification settings
4. Verify reviewer email addresses
5. Check for mail flow issues

---

## Escalation Path

If issues persist:

1. **First tier**: Communication Compliance Admin - policy configuration
2. **Second tier**: Purview Administrator - platform settings
3. **Third tier**: Legal/Compliance - escalation procedures
4. **Fourth tier**: Microsoft Support - platform issues

---

*Updated: January 2026 | Version: v1.2*
