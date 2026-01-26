# Troubleshooting: Control 1.1 - Restrict Agent Publishing by Authorization

**Last Updated:** January 2026

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| User can still create agents | Security group not applied | Verify group membership; check environment security roles |
| Authorized user cannot access | Group sync delay | Wait 15 minutes; have user sign out and back in |
| Publishing events not in audit | Audit not enabled or delay | Verify audit is enabled; wait 24-48 hours for new events |
| Cannot restrict Copilot Studio | Feature not available | Enable Managed Environments first ([Control 2.1](../../../controls/pillar-2-management/2.1-managed-environments.md)) |
| Sharing still works | Limit sharing not enabled | Enable in Managed Environment settings |
| Group membership not reflected | Entra ID sync delay | Wait up to 60 minutes for directory sync |
| Role assignment fails | Insufficient permissions | Verify you have Power Platform Admin role |

---

## Detailed Troubleshooting

### Issue: User Can Still Create Agents After Restriction

**Symptoms:** A user who should not have access can still create agents in Copilot Studio.

**Diagnostic Steps:**

1. Verify the user is NOT in the authorized security group:
   ```
   Entra Admin Center > Identity > Groups > [FSI-Agent-Makers-*] > Members
   ```

2. Check if the user has Environment Maker role directly assigned:
   ```powershell
   Get-AdminPowerAppEnvironmentRoleAssignment -EnvironmentName $EnvironmentName |
       Where-Object { $_.PrincipalDisplayName -eq "username" }
   ```

3. Verify the "Who can create and edit Copilots" setting is configured:
   ```
   PPAC > Environments > [env] > Settings > Features
   ```

4. Check if the user has Dataverse System Admin role (bypasses restrictions):
   ```powershell
   Get-AdminPowerAppEnvironmentRoleAssignment -EnvironmentName $EnvironmentName |
       Where-Object { $_.RoleType -eq "SystemAdministrator" }
   ```

**Resolution:** Remove direct role assignments; ensure user is not in an authorized group or has admin role.

---

### Issue: Authorized User Cannot Access Environment

**Symptoms:** A user in the authorized security group cannot create agents.

**Diagnostic Steps:**

1. Verify group membership is current (check timestamp)
2. Have user sign out completely and sign back in
3. Check for nested group issues (user in subgroup)
4. Verify the security group is added to the environment's "Who can create and edit Copilots" setting

**Resolution:**
- Wait 15-60 minutes for sync
- Ensure group is a Security group (not M365 group)
- Add user directly for immediate access while troubleshooting

---

### Issue: Publishing Events Not Appearing in Audit Log

**Symptoms:** Cannot find publish events in Microsoft Purview Audit.

**Diagnostic Steps:**

1. Verify Unified Audit Log is enabled:
   ```powershell
   Get-AdminAuditLogConfig | Select-Object UnifiedAuditLogIngestionEnabled
   ```

2. Check you're searching correct date range (events may have 24-48hr delay)

3. Verify correct search criteria:
   - Activity: "Published bot"
   - Record type: "PowerApps"

4. Check user has audit log search permissions

**Resolution:**
- Enable audit logging if disabled
- Expand search date range
- Wait 24-48 hours for new events to appear

---

### Issue: Cannot Enable Copilot Studio Restrictions

**Symptoms:** The "Who can create and edit Copilots" setting is not available.

**Diagnostic Steps:**

1. Verify environment is a Managed Environment:
   ```
   PPAC > Environments > [env] > Check for "Managed" badge
   ```

2. Check if Copilot Studio is enabled for the environment

3. Verify you have Power Platform Admin role

**Resolution:**
- Enable Managed Environments first (see [Control 2.1](../../../controls/pillar-2-management/2.1-managed-environments.md))
- Contact Microsoft support if feature not appearing in Managed Environment

---

## How to Confirm Configuration is Active

### Via Portal (Entra ID)

1. Navigate to **Identity** > **Groups** > Select FSI-Agent-Makers group
2. Verify correct members are listed
3. Check no unauthorized users have access

### Via Portal (Power Platform)

1. Navigate to **Manage** > **Environments** > Select environment
2. Go to **Settings** > **Users + permissions** > **Security roles**
3. Verify Environment Maker role is assigned only to authorized groups

### Via User Testing

1. Have an unauthorized user attempt to access Copilot Studio
2. Verify they cannot create or publish agents
3. Have an authorized user test full workflow

### Via PowerShell

```powershell
# Quick validation check
$EnvironmentName = "your-environment-id"

# Check Environment Maker assignments
Write-Host "Environment Maker Assignments:" -ForegroundColor Cyan
Get-AdminPowerAppEnvironmentRoleAssignment -EnvironmentName $EnvironmentName |
    Where-Object { $_.RoleType -eq "EnvironmentMaker" } |
    Format-Table PrincipalDisplayName, PrincipalType

# Check for "All Users" assignment (should be empty)
$allUsers = Get-AdminPowerAppEnvironmentRoleAssignment -EnvironmentName $EnvironmentName |
    Where-Object { $_.PrincipalType -eq "Tenant" -and $_.RoleType -eq "EnvironmentMaker" }

if ($allUsers) {
    Write-Host "WARNING: All Users still has Environment Maker role!" -ForegroundColor Red
} else {
    Write-Host "OK: All Users does not have Environment Maker role" -ForegroundColor Green
}
```

---

## Escalation Path

If issues persist after troubleshooting:

1. **Power Platform Admin Team** - For environment configuration issues
2. **Entra ID Admin Team** - For security group and role issues
3. **Microsoft Support** - For platform bugs or feature issues
4. **AI Governance Lead** - For policy interpretation questions

---

[Back to Control 1.1](../../../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
