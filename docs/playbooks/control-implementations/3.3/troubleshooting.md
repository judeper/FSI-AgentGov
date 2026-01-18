# Control 3.3: Compliance and Regulatory Reporting - Troubleshooting

> This playbook provides troubleshooting guidance for [Control 3.3](../../../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md).

---

## Common Issues and Resolutions

### Issue: Compliance Manager Data Not Syncing

**Symptoms:** Assessment scores not reflecting current state

**Resolution:**

1. Navigate to Compliance Manager > Settings
2. Check data connector status
3. Manually refresh assessment data
4. Verify improvement actions are properly assigned

---

### Issue: Report Distribution Fails

**Symptoms:** Recipients not receiving scheduled reports

**Resolution:**

1. Check Power Automate flow run history
2. Verify email addresses are correct
3. Check for mail flow rules blocking
4. Ensure service account has send permissions

---

### Issue: SharePoint Archive Permission Denied

**Symptoms:** Reports fail to save to archive library

**Resolution:**

1. Verify service account has Contribute permissions
2. Check library is not in read-only mode
3. Ensure retention labels allow new content
4. Test with manual upload first

---

### Issue: Examination Package Incomplete

**Symptoms:** Missing documents in generated package

**Resolution:**

1. Review MANIFEST.json for required documents
2. Verify source document locations
3. Check document permissions
4. Validate content freshness dates

---

### Issue: Dashboard Performance Slow

**Symptoms:** Power BI dashboard takes long to load

**Resolution:**

1. Implement incremental refresh
2. Optimize data model relationships
3. Reduce visual complexity
4. Consider Premium capacity for large datasets

---

## Diagnostic Commands

```powershell
# Check Compliance Manager connection
Get-MgComplianceManagement | Select-Object Status, LastSync

# Verify SharePoint permissions
Get-PnPListItem -List "Compliance Reports" -Query "<View><Query><Where><Eq><FieldRef Name='Author'/><Value Type='User'>ServiceAccount</Value></Eq></Where></Query></View>"

# Check Power Automate flow status
Get-AdminFlow -EnvironmentName "Default" | Where-Object { $_.DisplayName -like "*Compliance*" }
```

---

## Escalation Path

| Issue Severity | Escalate To | Response Time |
|----------------|-------------|---------------|
| Report generation failure | IT Operations | 4 hours |
| Compliance score incorrect | Compliance Officer | 24 hours |
| Regulatory deadline at risk | CCO | Immediate |
| Data sync issues | Microsoft Support | Per SLA |

---

## Next Steps

- [Portal Walkthrough](./portal-walkthrough.md) - Manual configuration
- [PowerShell Setup](./powershell-setup.md) - Automation scripts
- [Verification & Testing](./verification-testing.md) - Test procedures

---

*Updated: January 2026 | Version: v1.1*
