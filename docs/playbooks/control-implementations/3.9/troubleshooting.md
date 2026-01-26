# Control 3.9: Microsoft Sentinel Integration - Troubleshooting

> This playbook provides troubleshooting guidance for [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md).

---

## Common Issues and Resolutions

### Issue: Data Connector Not Receiving Data

**Symptoms:** Connector shows "Connected" but no data in tables

**Resolution:**

1. Verify source system is generating logs
2. Check diagnostic settings are enabled
3. Confirm Log Analytics workspace is correct
4. Allow 24 hours for initial data ingestion
5. Check for firewall blocking Azure endpoints

---

### Issue: Analytics Rule Not Triggering

**Symptoms:** Matching events exist but no alerts

**Resolution:**

1. Verify rule is enabled
2. Check query returns results manually
3. Verify time range covers recent data
4. Check trigger threshold setting
5. Review rule execution history

---

### Issue: High False Positive Rate

**Symptoms:** Too many alerts for normal activity

**Resolution:**

1. Refine KQL query with exclusions
2. Adjust baseline period length
3. Increase deviation threshold
4. Add entity allowlisting
5. Consider machine learning rules

---

### Issue: Workbook Performance Slow

**Symptoms:** Workbook takes long to load

**Resolution:**

1. Reduce query time range
2. Optimize KQL queries
3. Use materialized views
4. Implement pagination
5. Consider dedicated cluster

---

## Diagnostic KQL Queries

```kql
// Check data freshness by table
union withsource=TableName *
| summarize LastRecord = max(TimeGenerated) by TableName
| order by LastRecord desc

// Check ingestion latency
OfficeActivity
| where TimeGenerated > ago(1h)
| extend IngestionDelay = ingestion_time() - TimeGenerated
| summarize AvgDelay = avg(IngestionDelay) by bin(TimeGenerated, 5m)

// Rule execution history
SentinelHealth
| where TimeGenerated > ago(24h)
| where OperationName == "AlertRule"
| summarize Count = count() by Status, AlertRuleName
```

---

## Escalation Path

| Issue Severity | Escalate To | Response Time |
|----------------|-------------|---------------|
| No data ingestion | Azure Support | 4 hours |
| Rule execution failure | Security Operations | 4 hours |
| Performance degradation | Platform Admin | 24 hours |
| False positive review | AI Governance Lead | 48 hours |

---

## Next Steps

- [Portal Walkthrough](./portal-walkthrough.md) - Manual configuration
- [PowerShell Setup](./powershell-setup.md) - Automation scripts
- [Verification & Testing](./verification-testing.md) - Test procedures

---

*Updated: January 2026 | Version: v1.2*
