# Control 3.5: Cost Allocation and Budget Tracking - Troubleshooting

> This playbook provides troubleshooting guidance for [Control 3.5](../../../controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md).

---

## Common Issues and Resolutions

### Issue: Costs Not Appearing in Reports

**Symptoms:** Zero or missing cost data for some resources

**Resolution:**

1. Verify resource tagging is complete
2. Check billing cycle timing (24-48 hour delay)
3. Ensure Cost Management Reader role assigned
4. Verify subscription is in scope

---

### Issue: Budget Alerts Not Triggering

**Symptoms:** Exceeded budget but no alerts received

**Resolution:**

1. Verify alert recipients are valid
2. Check email spam/junk folders
3. Confirm budget scope matches resources
4. Test with lower threshold

---

### Issue: Incorrect Business Unit Attribution

**Symptoms:** Costs assigned to wrong cost center

**Resolution:**

1. Review environment naming convention
2. Check resource group tags
3. Verify cost allocation rules
4. Update mapping table

---

### Issue: License Utilization Data Stale

**Symptoms:** Usage data showing incorrect active counts

**Resolution:**

1. Verify Microsoft Graph permissions
2. Check report refresh schedule
3. Confirm audit logging is enabled
4. Allow 72 hours for data population

---

## Diagnostic Commands

```powershell
# Check Azure cost management access
Get-AzRoleAssignment | Where-Object { $_.RoleDefinitionName -like "*Cost*" }

# Verify environment tags
Get-AdminPowerAppEnvironment | Select-Object DisplayName, EnvironmentType

# Check budget status
Get-AzConsumptionBudget | Format-Table Name, Amount, CurrentSpend

# Test Graph access for license data
Get-MgSubscribedSku | Select-Object SkuPartNumber, ConsumedUnits
```

---

## Escalation Path

| Issue Severity | Escalate To | Response Time |
|----------------|-------------|---------------|
| Budget exceeded 100% | Finance + BU Owner | Immediate |
| Cost allocation errors | IT Finance | 24 hours |
| Reporting system down | Platform Admin | 4 hours |
| License audit findings | Compliance | 48 hours |

---

## Next Steps

- [Portal Walkthrough](./portal-walkthrough.md) - Manual configuration
- [PowerShell Setup](./powershell-setup.md) - Automation scripts
- [Verification & Testing](./verification-testing.md) - Test procedures

---

*Updated: January 2026 | Version: v1.2*
