# Troubleshooting: Control 3.2 - Usage Analytics and Activity Monitoring

**Last Updated:** January 2026

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| Missing usage data | Managed Environment not enabled or data latency | Enable Managed Environment; wait 24-48 hours for initial data |
| Alerts not triggering | Recipients not configured or email filtering | Verify alert is enabled; check notification settings |
| Incorrect success rates | Metric includes all session types | Filter by interaction type for customer-facing metrics |
| Audit log gaps | Log latency or search scope issues | Audit logs may take 24 hours; expand search date range |
| Dashboard timeout | Large data volume | Apply environment filters; reduce date range |

---

## Detailed Troubleshooting

### Issue: Missing Usage Data on Dashboard

**Symptoms:** Dashboard shows no metrics or incomplete data for agents.

**Diagnostic Steps:**

1. Verify Managed Environment is enabled:
   ```powershell
   Get-AdminPowerAppEnvironment -EnvironmentName "env-id" |
       Select-Object DisplayName, @{N='IsManaged';E={$_.Properties.isManaged}}
   ```

2. Check data freshness - look for "Last Updated" timestamp on dashboard

3. Verify you have appropriate permissions to view the environment

4. Confirm agents have recent activity (no data if agents are inactive)

**Resolution:**
- Enable Managed Environments for usage insights
- Wait 24-48 hours for initial data population
- Verify Power Platform Administrator role assignment

---

### Issue: Alerts Not Triggering

**Symptoms:** Conditions are met but no notifications are received.

**Diagnostic Steps:**

1. Navigate to PPAC > Monitor > Alerts
2. Verify the alert rule is in "Enabled" state
3. Check notification recipient configuration
4. Review the alert condition logic

5. Test email delivery:
   - Check spam/junk folders
   - Add PPAC sender to safe list
   - Verify email addresses are correct

**Resolution:**
- Enable the alert rule if disabled
- Configure valid notification recipients
- Add `noreply@microsoft.com` to safe senders
- Test with a simple alert that triggers easily

---

### Issue: Incorrect Success Rates Reported

**Symptoms:** Reported success rates do not match observed agent behavior.

**Diagnostic Steps:**

1. Understand the metric calculation:
   - Success rate includes ALL session types
   - Failed handoffs count as failures
   - Abandoned sessions may affect rate

2. Review session definitions in documentation

3. Compare with Copilot Studio built-in analytics

4. Check for environment or agent filter issues

**Resolution:**
- Filter by specific interaction types for accurate metrics
- Use Copilot Studio analytics for agent-specific details
- Document calculation methodology for auditors

---

### Issue: Audit Log Gaps

**Symptoms:** Missing entries for specific time periods in audit logs.

**Diagnostic Steps:**

1. Check audit log ingestion latency:
   - Logs may take up to 24 hours to appear
   - Peak times may cause additional delays

2. Verify search parameters:
   ```powershell
   # Expand date range to verify data exists
   Search-UnifiedAuditLog `
       -StartDate (Get-Date).AddDays(-7) `
       -EndDate (Get-Date) `
       -RecordType PowerApps `
       -ResultSize 100
   ```

3. Check RecordType filter is correct for your search

4. Verify your role has audit log search permissions

**Resolution:**
- Wait 24-48 hours for recent events to appear
- Expand search date range
- Use correct RecordType (PowerApps, CopilotStudio)
- Request Compliance Administrator role if needed

---

### Issue: Performance Dashboard Timeout

**Symptoms:** Dashboard fails to load or times out when accessing metrics.

**Diagnostic Steps:**

1. Check the scope of your query:
   - Number of environments selected
   - Date range specified
   - Number of agents included

2. Try with a narrower scope:
   - Single environment
   - Shorter date range (7 days vs 30 days)

3. Check browser performance and network connectivity

**Resolution:**
- Apply environment filters to reduce data volume
- Reduce date range for initial load
- Schedule reports instead of real-time queries
- Use PowerShell for large data exports

---

### Issue: Usage Insights Email Not Received

**Symptoms:** Weekly digest email not arriving despite configuration.

**Diagnostic Steps:**

1. Verify Managed Environment has usage insights enabled:
   - Navigate to Environment > Edit Managed Environment
   - Check "Include insights for this environment in the weekly email digest"

2. Verify recipient email addresses are correct

3. Check spam/junk email folders

4. Confirm the environment has activity to report

**Resolution:**
- Enable usage insights in Managed Environment settings
- Add correct recipient email addresses
- Add Microsoft sender to safe list
- Wait for next weekly digest cycle

---

## How to Confirm Configuration is Active

### Via Portal (PPAC)

1. Navigate to **Monitor** > **Overview**
2. Verify summary cards show current data
3. Check **Alerts** for enabled rules
4. Review **Copilot Studio** for agent metrics

### Via Portal (Purview)

1. Navigate to [Microsoft Purview](https://compliance.microsoft.com) > Audit
2. Search for recent Power Platform activities
3. Verify entries are appearing for current date

### Via PowerShell

```powershell
# Quick validation check
Write-Host "Checking Control 3.2 Configuration..." -ForegroundColor Cyan

# Check environment access
$envCount = (Get-AdminPowerAppEnvironment).Count
Write-Host "Accessible environments: $envCount"

# Check managed environments
$managedCount = (Get-AdminPowerAppEnvironment |
    Where-Object { $_.Properties.isManaged -eq $true }).Count
Write-Host "Managed environments: $managedCount"

# Check app visibility
$appCount = (Get-AdminPowerApp).Count
Write-Host "Visible Power Apps: $appCount"

# Check recent audit logs
try {
    $recentLogs = Search-UnifiedAuditLog `
        -StartDate (Get-Date).AddDays(-1) `
        -EndDate (Get-Date) `
        -RecordType PowerApps `
        -ResultSize 10
    Write-Host "Recent audit log entries: $($recentLogs.Count)"
} catch {
    Write-Host "Audit log access issue" -ForegroundColor Yellow
}
```

---

## Escalation Path

If issues persist after troubleshooting:

1. **Power Platform Admin Team** - For PPAC access and monitoring configuration
2. **Purview Admin Team** - For audit log access and retention issues
3. **Microsoft Support** - For platform bugs or feature issues
4. **AI Governance Lead** - For policy and process questions
5. **Compliance Officer** - For regulatory implications of monitoring gaps

---

[Back to Control 3.2](../../../controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
