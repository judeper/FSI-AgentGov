# Control 1.7: Comprehensive Audit Logging - Troubleshooting

> This playbook provides troubleshooting guidance for [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md).

---

## Common Issues

### Issue: No Audit Events Appearing in Search

**Symptoms:** Audit search returns empty results despite known activity

**Solutions:**

1. Verify unified audit logging is enabled (Set-AdminAuditLogConfig)
2. Confirm you are searching **UTC** time range
3. Check date range and ingestion latency (30 min to 24 hours)
4. Verify you have appropriate permissions (Compliance Administrator)
5. Try a broad search (no filters) to confirm any audit data exists
6. Validate via PowerShell using `Search-UnifiedAuditLog`

---

### Issue: Copilot Events Not Being Logged

**Symptoms:** Other audit events appear but no CopilotInteraction records

**Solutions:**

1. Verify users have Microsoft 365 Copilot licenses assigned
2. Confirm Copilot is actually being used (not just licensed)
3. Search broadly first, then narrow to specific activities
4. Wait longer - Copilot events may have additional latency
5. Verify the activity is part of audited workloads for your tenant

---

### Issue: Expected Events Missing (Partial Results)

**Symptoms:** Some audit events appear but specific activities are missing

**Solutions:**

1. Remove restrictive filters first and confirm time range returns results
2. Confirm date/time range is in **UTC**
3. Broaden search window to account for ingestion latency
4. Validate the same query via PowerShell
5. Check operation names match what your tenant emits

---

### Issue: Audit Log Export Fails or Incomplete

**Symptoms:** Export times out or contains fewer records than expected

**Solutions:**

1. Reduce date range to smaller chunks
2. Add filters to reduce result set size
3. Use PowerShell instead of portal for large exports
4. Check for rate limiting (wait and retry)
5. Verify network connectivity and session timeout

---

### Issue: Extended Retention Not Working

**Symptoms:** Old audit events are missing despite retention policy

**Solutions:**

1. Verify retention policy is properly configured and enabled
2. Check policy priority if multiple policies exist
3. Confirm users are assigned E5/E5 Compliance licenses
4. Review policy scope (ensure it covers needed record types)
5. Contact Microsoft Support for retention investigation

---

### Issue: SIEM Integration Missing Events

**Symptoms:** Some audit events not appearing in Sentinel/SIEM

**Solutions:**

1. Verify data connector is properly configured
2. Check for ingestion delays (5-15 minutes)
3. Review connector health in Sentinel
4. Verify record types are included in connector config
5. Validate end-to-end by correlating known audit records

---

## Escalation Path

If issues persist:

1. **First tier**: Purview Audit Admin - verify configuration
2. **Second tier**: Security Operations - check SIEM integration
3. **Third tier**: Microsoft Support - platform-level issues

---

*Updated: January 2026 | Version: v1.2*
