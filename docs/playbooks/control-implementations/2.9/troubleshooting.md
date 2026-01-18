# Troubleshooting: Control 2.9 - Agent Performance Monitoring and Optimization

**Last Updated:** January 2026

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| No analytics data | Analytics disabled | Enable in PPAC settings |
| Dashboard blank | Data source disconnected | Refresh Power BI connection |
| Alerts not firing | Flow disabled or threshold too high | Check flow status and thresholds |
| Export failing | Storage permissions | Verify Azure RBAC permissions |

---

## Detailed Troubleshooting

### Issue: Copilot Studio Analytics Empty

**Symptoms:** No sessions, conversations, or metrics visible

**Resolution:**

1. Verify analytics is enabled in Power Platform Admin Center
2. Check that agents have been used (need interaction data)
3. Wait 24-48 hours for initial data population
4. Verify user has appropriate permissions to view analytics

---

### Issue: Power BI Dashboard Not Refreshing

**Symptoms:** Dashboard shows stale data or errors

**Resolution:**

1. Check data source credentials in Power BI
2. Verify data gateway is running (if using on-premises data)
3. Check for errors in refresh history
4. Manually trigger refresh to see error details
5. Update connection strings if source moved

---

### Issue: Alert Flow Not Triggering

**Symptoms:** Thresholds exceeded but no notification received

**Resolution:**

1. Verify Power Automate flow is enabled
2. Check flow run history for errors
3. Verify threshold conditions match data format
4. Test with lower threshold to confirm flow works
5. Check notification channel (email/Teams) is valid

---

### Issue: Performance Degradation Detected

**Symptoms:** Error rates or response times exceeding thresholds

**Resolution:**

1. Check recent changes to agent configuration
2. Review conversation logs for error patterns
3. Verify backend services (APIs, data sources) are healthy
4. Check for capacity issues in environment
5. Roll back recent changes if necessary

---

## Escalation Path

1. **Agent Owner** - Agent-specific issues
2. **Power Platform Admin** - Analytics and environment
3. **AI Governance Lead** - KPI definitions, trend analysis
4. **Operations Team** - Incident response

---

## Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| Analytics delay | 24-48 hour initial population | Plan for delay in new deployments |
| CSAT requires prompt | Users must rate | Enable satisfaction survey in agent |
| Cross-environment views | Separate dashboards needed | Create tenant-level Power BI dashboard |
| Real-time not available | Minimum 15-min delay | Use Azure Monitor for true real-time |

---

[Back to Control 2.9](../../../controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
