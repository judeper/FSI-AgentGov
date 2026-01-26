# Control 4.5: SharePoint Security and Compliance Monitoring - Troubleshooting

> This playbook provides troubleshooting guidance for [Control 4.5](../../../controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md).

---

## Common Issues and Solutions

| Issue | Symptoms | Solution |
|-------|----------|----------|
| **Agent insights not appearing** | "View reports" shows no data or errors | Verify SharePoint Advanced Management license is assigned; data may take 24-48 hours to populate initially |
| **Data access reports empty** | Reports generate but show no content | Ensure site activity exists; run "Get started" to initialize baseline if first use |
| **Dashboard cards missing data** | Home dashboard shows blanks or errors | Check SharePoint Admin role assignment; verify browser isn't blocking scripts |
| **Audit log search returns no results** | Search completes but finds nothing | Verify unified audit logging is enabled; check date range (max 90 days for standard) |
| **Advanced management features unavailable** | Features grayed out or missing | Confirm SharePoint Advanced Management license; some features require E5 |
| **Export failures** | Report export times out or fails | Reduce date range; filter by specific users or operations; try during off-peak hours |
| **Real-time alerts not triggering** | Expected alerts not received | Check alert policy configuration; verify recipient email; review alert threshold settings |

---

## Diagnostic Steps

### 1. Verify Licensing

```powershell
Get-MgSubscribedSku | Where-Object {
    $_.SkuPartNumber -like "*SPE_E5*" -or
    $_.SkuPartNumber -like "*SHAREPOINTENTERPRISE*"
}
```

### 2. Check Audit Logging Status

```powershell
Get-AdminAuditLogConfig | Select-Object UnifiedAuditLogIngestionEnabled
```

### 3. Verify SharePoint Admin Access

```powershell
Get-MgUserMemberOf -UserId "admin@contoso.com" |
    Where-Object { $_.AdditionalProperties.displayName -like "*SharePoint*" }
```

### 4. Test Report Generation

1. Navigate to SharePoint Admin Center > Reports > Data access governance
2. Click "Get started" to run initial assessment
3. Wait for completion (may take several hours for large tenants)

---

## Escalation Path

| Issue Severity | Escalation Path | SLA |
|---------------|-----------------|-----|
| Reports not loading after 48 hours | SharePoint Admin > Microsoft Support | 2 business days |
| Audit logging gaps | Security Admin > Purview Support | 1 business day |
| Agent insights missing for licensed tenant | SharePoint Admin > Microsoft Support | 2 business days |
| Real-time monitoring failures | Security Operations > Microsoft Support | Same day |

---

## Prevention Best Practices

1. **Verify licensing** before relying on advanced features
2. **Enable audit logging** at tenant setup
3. **Schedule regular checks** of monitoring capabilities
4. **Document baseline metrics** for comparison
5. **Test exports periodically** to ensure data retrieval works
6. **Configure redundant alerting** for critical events

---

## Related Resources

- [Agent insights in SharePoint](https://learn.microsoft.com/en-us/sharepoint/insights-on-sharepoint-agents)
- [Data access governance reports](https://learn.microsoft.com/en-us/sharepoint/data-access-governance-reports)
- [SharePoint Advanced Management overview](https://learn.microsoft.com/en-us/sharepoint/advanced-management)
- [Microsoft Purview Audit overview](https://learn.microsoft.com/en-us/purview/audit-solutions-overview)

---

*Updated: January 2026 | Version: v1.2*
