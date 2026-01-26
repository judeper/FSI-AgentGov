# Control 1.9: Data Retention and Deletion Policies - Troubleshooting

> This playbook provides troubleshooting guidance for [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md).

---

## Common Issues

### Issue: Retention Policy Not Applying

**Symptoms:** Content not being retained as expected

**Solutions:**

1. Verify policy is enabled and distributed
2. Check location scope includes target content
3. Allow propagation time (up to 7 days)
4. Verify no conflicting policies
5. Check for exclusions in policy

---

### Issue: Content Deleted Before Retention End

**Symptoms:** Items missing before retention period expires

**Solutions:**

1. Check for user or admin deletion
2. Verify retention policy scope
3. Review if legal hold should apply
4. Check audit log for deletion events
5. Verify retention action is "Keep" not just "Delete"

---

### Issue: Disposition Review Not Triggering

**Symptoms:** Content at retention end not appearing for review

**Solutions:**

1. Verify label has disposition review action
2. Check disposition reviewers are configured
3. Confirm label is applied to content
4. Review retention start date calculation
5. Allow time for processing

---

### Issue: Cannot Delete Content After Retention

**Symptoms:** Content stuck even after retention period

**Solutions:**

1. Check for legal hold on content
2. Verify disposition review was completed
3. Check for regulatory record flag
4. Review if preservation lock is enabled
5. Contact compliance for manual disposition

---

### Issue: Policy Distribution Failing

**Symptoms:** Policy shows "Error" or "Pending" status

**Solutions:**

1. Check for invalid location references
2. Verify permissions for policy creation
3. Review policy for conflicting settings
4. Check service health dashboard
5. Retry distribution after 24 hours

---

### Issue: Label Not Available for Selection

**Symptoms:** Published labels not appearing in locations

**Solutions:**

1. Verify label policy includes target location
2. Allow propagation time (up to 24 hours)
3. Check user permissions to apply labels
4. Verify label is published, not draft
5. Clear browser cache and retry

---

### Issue: Legal Hold Not Preventing Deletion

**Symptoms:** Content on hold still being deleted

**Solutions:**

1. Verify hold is active and scoped correctly
2. Check hold query filters
3. Confirm content location matches hold scope
4. Review if hold was accidentally released
5. Check for superseding admin actions

---

## SEC 17a-4 WORM Compliance

**Important:** Standard Microsoft 365 retention policies do not meet SEC 17a-4(f) WORM requirements. For broker-dealers:

1. Use Preservation Lock for immutable retention
2. Consider third-party archiving solutions
3. Obtain written attestation from vendor
4. Document WORM compliance procedures

---

## Escalation Path

If issues persist:

1. **First tier**: Records Management - retention label and policy issues
2. **Second tier**: Purview Administrator - distribution and configuration
3. **Third tier**: Legal - hold and disposition decisions
4. **Fourth tier**: Microsoft Support - platform-level issues

---

*Updated: January 2026 | Version: v1.2*
