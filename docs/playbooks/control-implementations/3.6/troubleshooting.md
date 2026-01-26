# Control 3.6: Orphaned Agent Detection and Remediation - Troubleshooting

> This playbook provides troubleshooting guidance for [Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md).

---

## Common Issues and Resolutions

### Issue: False Positives in Detection

**Symptoms:** Active agents flagged as orphaned

**Resolution:**

1. Verify user lookup against correct Entra ID tenant
2. Check for guest vs. member user types
3. Adjust inactivity threshold if too aggressive
4. Add exclusions for service accounts

---

### Issue: Reassignment Fails

**Symptoms:** Unable to transfer ownership

**Resolution:**

1. Verify new owner has appropriate license
2. Check environment access permissions
3. Ensure new owner exists in tenant
4. Try using Admin PowerShell module

---

### Issue: Archived Agent Still Accessible

**Symptoms:** Disabled agent still responding

**Resolution:**

1. Verify disable command completed
2. Check for cached sessions
3. Clear CDN cache if applicable
4. Force refresh agent status

---

### Issue: Detection Script Timeout

**Symptoms:** Script fails on large tenant

**Resolution:**

1. Run detection by environment batches
2. Increase PowerShell timeout
3. Use pagination for large user lists
4. Consider parallel processing

---

## Diagnostic Commands

```powershell
# Verify agent status
Get-AdminPowerApp -AppName "agent-id" -EnvironmentName "environment" | Select-Object DisplayName, AppType, IsDeleted

# Check user status
Get-MgUser -UserId "owner@company.com" | Select-Object DisplayName, AccountEnabled

# List disabled agents
Get-AdminPowerApp -EnvironmentName "environment" | Where-Object { $_.Internal.properties.isDisabled -eq $true }
```

---

## Escalation Path

| Issue Severity | Escalate To | Response Time |
|----------------|-------------|---------------|
| Detection failure | Platform Admin | 4 hours |
| Ownership dispute | AI Governance Lead | 24 hours |
| Data loss risk | Compliance + Legal | Immediate |
| Bulk orphan discovery | Director | 4 hours |

---

## Next Steps

- [Portal Walkthrough](./portal-walkthrough.md) - Manual configuration
- [PowerShell Setup](./powershell-setup.md) - Automation scripts
- [Verification & Testing](./verification-testing.md) - Test procedures

---

*Updated: January 2026 | Version: v1.2*
