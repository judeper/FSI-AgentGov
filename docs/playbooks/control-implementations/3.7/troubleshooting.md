# Control 3.7: PPAC Security Posture Assessment - Troubleshooting

> This playbook provides troubleshooting guidance for [Control 3.7](../../../controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md).

---

## Common Issues and Resolutions

### Issue: Security Dashboard Not Loading

**Symptoms:** Security page shows error or blank

**Resolution:**

1. Verify Power Platform Admin role assignment
2. Clear browser cache
3. Try different browser
4. Check for service health issues

---

### Issue: Recommendations Not Updating

**Symptoms:** Completed actions still show as open

**Resolution:**

1. Allow 24-48 hours for sync
2. Refresh the dashboard
3. Verify change was applied correctly
4. Check environment scope

---

### Issue: Score Not Reflecting Changes

**Symptoms:** Security score unchanged after improvements

**Resolution:**

1. Verify all components of scoring
2. Check for conflicting policies
3. Re-run assessment script
4. Contact Microsoft Support if persists

---

### Issue: Audit Logs Not Appearing

**Symptoms:** Monitor tab shows no data

**Resolution:**

1. Verify audit logging is enabled
2. Check date range filter
3. Confirm user has audit log access
4. Allow time for log ingestion

---

## Diagnostic Commands

```powershell
# Check admin role
Get-AdminPowerAppEnvironment | Select-Object DisplayName, IsAdmin

# Verify DLP policies exist
Get-DlpPolicy | Format-Table DisplayName, PolicyType

# Check managed environment status
Get-AdminPowerAppEnvironment | Select-Object DisplayName, @{N='IsManaged';E={$_.Internal.properties.governanceConfiguration.enableManagedEnvironment}}
```

---

## Escalation Path

| Issue Severity | Escalate To | Response Time |
|----------------|-------------|---------------|
| Dashboard failure | Microsoft Support | 4 hours |
| Score calculation error | Platform Admin | 24 hours |
| Missing recommendations | AI Governance Lead | 48 hours |
| Audit log gaps | Security Team | Immediate |

---

## Next Steps

- [Portal Walkthrough](./portal-walkthrough.md) - Manual configuration
- [PowerShell Setup](./powershell-setup.md) - Automation scripts
- [Verification & Testing](./verification-testing.md) - Test procedures

---

*Updated: January 2026 | Version: v1.2*
