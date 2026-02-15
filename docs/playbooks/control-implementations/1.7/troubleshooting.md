# Control 1.7: Comprehensive Audit Logging - Troubleshooting

> This playbook provides troubleshooting guidance for [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md).

---

## Common Issues

### Issue: No Audit Events Appearing in Search

**Symptoms:** Audit search returns empty results despite known activity

**Solutions:**

1. Verify unified audit logging is enabled (use `Get-AdminAuditLogConfig` — see diagnostic script below)
2. Confirm you are searching **UTC** time range
3. Check date range and ingestion latency (30 min to 24 hours)
4. Verify you have appropriate permissions (Purview Compliance Admin)
5. Try a broad search (no filters) to confirm any audit data exists
6. Validate via PowerShell using `Search-UnifiedAuditLog`

**Diagnostic Script:**

```powershell
# Connect to Exchange Online (not IPPSSession) for config cmdlets
Connect-ExchangeOnline -UserPrincipalName admin@contoso.com

# Check if unified audit logging is enabled
Get-AdminAuditLogConfig | Select-Object UnifiedAuditLogIngestionEnabled
# Expected: True

# Check if mailbox auditing is enabled
Get-OrganizationConfig | Select-Object AuditDisabled
# Expected: False

# If audit logging is disabled, enable it:
# Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $true

Disconnect-ExchangeOnline -Confirm:$false
```

---

### Issue: Copilot Events Not Being Logged

**Symptoms:** Other audit events appear but no CopilotInteraction records

**Solutions:**

1. Verify users have Microsoft 365 Copilot licenses assigned
2. Confirm Copilot is actually being used (not just licensed)
3. Search broadly first, then narrow to specific activities
4. Wait longer - Copilot events may have additional latency
5. Verify the activity is part of audited workloads for your tenant

**Diagnostic Script:**

```powershell
# Connect to Security & Compliance for audit search
Connect-IPPSSession -UserPrincipalName admin@contoso.com

# Broad search to confirm any audit data exists
$allEvents = Search-UnifiedAuditLog -StartDate (Get-Date).AddDays(-7) -EndDate (Get-Date) -ResultSize 10
if ($null -eq $allEvents) {
    Write-Warning "No audit events found at all - check if audit logging is enabled"
} else {
    Write-Host "Audit logging is working. Checking for Copilot events..."
    $copilotEvents = Search-UnifiedAuditLog -StartDate (Get-Date).AddDays(-7) -EndDate (Get-Date) `
        -RecordType CopilotInteraction -ResultSize 10
    if ($null -eq $copilotEvents) {
        Write-Warning "No CopilotInteraction events - verify users have Copilot licenses and are actively using Copilot"
    } else {
        Write-Host "Found $(@($copilotEvents).Count) Copilot events"
    }
}

Disconnect-ExchangeOnline -Confirm:$false
```

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

### Issue: Dataverse Environment Auditing Not Capturing Events

**Symptoms:** Dataverse entity changes or user sign-ins not appearing in audit logs

**Solutions:**

1. Verify environment-level auditing is enabled: **PPAC** > **Environments** > select environment > **Settings** > **Audit and logs** > **Audit settings** > "Start Auditing" must be enabled
2. Verify tenant-level auditing: **PPAC** > **Security** > **Compliance** > **Auditing** > both "User Sign-In" and "Activity" must be enabled
3. Check audit log retention is set to ≥180 days
4. Ensure auditing is enabled on the specific Dataverse tables/entities you expect to see
5. Allow for ingestion latency (may take up to several hours for Dataverse events)

---

### Issue: PowerShell Connection Failures

**Symptoms:** `Connect-ExchangeOnline` or `Connect-IPPSSession` fails with authentication or module errors

**Common error messages:**

- `"The term 'Connect-ExchangeOnline' is not recognized"` — Module not installed
- `"AADSTS50076: Due to a configuration change made by your administrator"` — MFA required
- `"New-ExoPSSession: Access is denied"` — Insufficient permissions

**Solutions:**

1. Install or update the module: `Install-Module ExchangeOnlineManagement -MinimumVersion 3.0.0 -Force`
2. For MFA-enabled accounts, use `Connect-ExchangeOnline` without `-Credential` (opens browser prompt)
3. Verify your account has the required admin roles (Purview Audit Admin, Exchange Online Admin)
4. If behind a proxy, configure PowerShell proxy settings before connecting
5. Try `-ShowBanner:$false` to suppress banner output that may interfere with automation

---

## Escalation Path

If issues persist:

1. **First tier**: Purview Audit Admin - verify configuration
2. **Second tier**: Security Operations - check SIEM integration
3. **Third tier**: Microsoft Support - platform-level issues

---

## Related Playbooks

- [Portal Walkthrough](portal-walkthrough.md) — Step-by-step portal configuration
- [PowerShell Setup](powershell-setup.md) — PowerShell scripts and automation
- [Verification & Testing](verification-testing.md) — Verification procedures and evidence collection
- [Purview Audit Query Pack](../../monitoring-and-validation/purview-audit-query-pack.md) — Saved audit searches and evidence collection

!!! tip "Automated Validation Available"
    For automated audit configuration validation, drift detection, and approval-gated remediation, see the [Audit Compliance Manager (ACM)](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/audit-compliance-manager) solution.

---

*Updated: February 2026 | Version: v1.3*
