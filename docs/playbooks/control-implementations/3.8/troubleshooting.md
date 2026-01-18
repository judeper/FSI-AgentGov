# Control 3.8: Copilot Hub and Governance Dashboard - Troubleshooting

> This playbook provides troubleshooting guidance for [Control 3.8](../../../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md).

---

## Common Issues and Resolutions

### Issue: Copilot Section Not Visible

**Symptoms:** Copilot not in M365 Admin Center navigation

**Resolution:**

1. Verify M365 Copilot licenses assigned in tenant
2. Ensure user has Global Admin or M365 Admin role
3. Clear browser cache and refresh
4. Check for tenant-level service issues

---

### Issue: Settings Changes Not Applying

**Symptoms:** Configuration updates don't reflect for users

**Resolution:**

1. Allow 24-48 hours for policy propagation
2. Have users sign out and back in
3. Check for conflicting Conditional Access policies
4. Verify no Group Policy overrides

---

### Issue: Agent Registry Incomplete

**Symptoms:** Missing agents or incorrect counts

**Resolution:**

1. Verify Entra ID sync is current
2. Check agents are properly registered
3. Use Refresh button on Registry page
4. Allow time for data population

---

### Issue: Usage Reports Empty

**Symptoms:** No data in usage reports

**Resolution:**

1. Confirm Copilot actively used (72+ hours)
2. Verify audit logging is enabled
3. Check report date range includes active usage
4. Verify Reports Reader role assigned

---

### Issue: PowerShell Scripts Failing

**Symptoms:** Authentication or permission errors

**Resolution:**

1. Update Microsoft.Graph module to latest
2. Verify required scopes are consented
3. Check Conditional Access policies
4. Re-authenticate with Connect-MgGraph

---

## Diagnostic Commands

```powershell
# Verify Copilot license assignment
Get-MgUser -Filter "assignedLicenses/any()" -All |
    Where-Object { $_.AssignedLicenses.SkuId -like "*copilot*" } |
    Select-Object DisplayName, UserPrincipalName

# Check admin role assignments
Get-MgDirectoryRole | Where-Object { $_.DisplayName -like "*Admin*" }

# Verify Graph connection
Get-MgContext | Select-Object Account, TenantId, Scopes
```

---

## Escalation Path

| Issue Severity | Escalate To | Response Time |
|----------------|-------------|---------------|
| Copilot section unavailable | Microsoft Support | 4 hours |
| Settings not propagating | IT Operations | 24 hours |
| Agent registry issues | Platform Admin | 4 hours |
| Compliance concern | Compliance Officer | Immediate |

---

## Next Steps

- [Portal Walkthrough](./portal-walkthrough.md) - Manual configuration
- [PowerShell Setup](./powershell-setup.md) - Automation scripts
- [Verification & Testing](./verification-testing.md) - Test procedures

---

*Updated: January 2026 | Version: v1.1*
