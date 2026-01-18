# Verification & Testing: Control 2.9 - Agent Performance Monitoring and Optimization

**Last Updated:** January 2026

## Manual Verification Steps

### Test 1: Verify Analytics Data Flow

1. Open Power Platform Admin Center > Analytics > Copilot Studio
2. Select a Zone 2 or Zone 3 agent
3. Review sessions, resolution rate, and CSAT data
4. **EXPECTED:** Data present for past 7+ days

### Test 2: Verify Dashboard Accuracy

1. Open Power BI Agent-Performance-Analytics workspace
2. Compare dashboard KPIs to raw data in PPAC
3. Verify refresh timestamp is recent
4. **EXPECTED:** Dashboard matches source data within refresh window

### Test 3: Test Alert Triggering

1. Temporarily lower error rate threshold (e.g., to 0.1%)
2. Wait for scheduled alert flow to run
3. Verify notification received
4. **EXPECTED:** Alert sent to configured recipients

### Test 4: Verify Data Export

1. Navigate to Azure Data Lake storage
2. Check for recent analytics export files
3. Verify data completeness
4. **EXPECTED:** Daily exports present with expected tables

---

## Test Cases

| Test ID | Scenario | Expected Result | Pass/Fail |
|---------|----------|-----------------|-----------|
| TC-2.9-01 | Analytics shows agent data | Sessions/CSAT visible | |
| TC-2.9-02 | Dashboard displays KPIs | All cards populated | |
| TC-2.9-03 | Alert triggers on threshold breach | Notification received | |
| TC-2.9-04 | Data export running | Files in Azure storage | |
| TC-2.9-05 | Review meetings scheduled | Calendar invites exist | |

---

## Evidence Collection Checklist

- [ ] Screenshot: Copilot Studio analytics dashboard
- [ ] Screenshot: Power BI KPI cards
- [ ] Screenshot: Alert notification (email or Teams)
- [ ] Screenshot: Azure Data Lake export files
- [ ] Document: Review meeting schedule
- [ ] Export: Sample performance data (CSV)

---

## Attestation Statement Template

```markdown
## Control 2.9 Attestation - Agent Performance Monitoring and Optimization

**Organization:** [Organization Name]
**Control Owner:** [Name/Role]
**Date:** [Date]

I attest that:

1. Copilot Studio analytics is enabled and collecting data
2. Performance KPIs are defined for each governance tier:
   - Tier 1: Error rate < [X]%, Response time < [X]s
   - Tier 2: Error rate < [X]%, Response time < [X]s, CSAT > [X]
   - Tier 3: Error rate < [X]%, Response time < [X]s, CSAT > [X]
3. Power BI dashboard is operational:
   - Workspace: [Name]
   - Refresh frequency: [Hourly/Daily]
   - Last refresh: [Timestamp]
4. Alerting is configured:
   - Error rate alerts: Enabled
   - Response time alerts: [Enabled/Disabled]
   - Recipients: [Email/Teams channel]
5. Review cadence is established:
   - Weekly operational: [Day/Time]
   - Monthly business: [Day/Time]
   - Quarterly executive: [Day/Time]

**Last Performance Review:** [Date]
**Agents Monitored:** [Count]

**Signature:** _______________________
**Date:** _______________________
```

---

[Back to Control 2.9](../../../controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
