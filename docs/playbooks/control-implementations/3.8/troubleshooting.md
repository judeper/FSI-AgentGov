# Control 3.8: Copilot Hub and Governance Dashboard - Troubleshooting

> This playbook provides troubleshooting guidance for [Control 3.8](../../../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md).

---

## Common Issues and Resolutions

### AI Feature Access Control Issues

#### Issue: User Still Has Copilot Access After Being Added to Exclusion Group

**Symptoms:** User added to `CopilotForM365AdminExclude` group can still access Copilot features

**Resolution:**

1. **Verify propagation time:**
   - Admin Exclusion Group membership changes take up to **24 hours** to propagate
   - Check timestamp of when user was added to group
   - If less than 24 hours, wait for full propagation window
   - Have user sign out and back in after 24-hour window

2. **Verify group name is exact:**
   - Navigate to Microsoft Entra admin center > Groups
   - Confirm group name is exactly `CopilotForM365AdminExclude` (case-sensitive)
   - Check for typos, extra spaces, or incorrect capitalization
   - If incorrect, create new group with correct name and migrate members

3. **Verify group membership:**
   - Open the exclusion group
   - Confirm user appears in Members list
   - Check for nested group issues (if using nested groups, verify membership cascades correctly)
   - Use PowerShell to verify: `Get-MgGroupMember -GroupId <GroupId> | Where-Object { $_.Id -eq '<UserId>' }`

4. **Check for conflicting policies:**
   - Verify no Conditional Access policies or other admin center settings override the exclusion
   - Check if user has multiple M365 Copilot license assignments from different sources
   - Review admin roles assigned to user (Global Admins may bypass certain restrictions)

5. **Force token refresh:**
   - Have user sign out of all Microsoft 365 sessions
   - Clear browser cache and cookies
   - Sign back in and test Copilot access
   - May require device restart for full token refresh

**Diagnostic Command:**
```powershell
# Verify user is in exclusion group
$group = Get-MgGroup -Filter "displayName eq 'CopilotForM365AdminExclude'"
$user = Get-MgUser -Filter "userPrincipalName eq 'user@contoso.com'"
Get-MgGroupMember -GroupId $group.Id | Where-Object { $_.Id -eq $user.Id }
```

---

#### Issue: Deployment Group Not Limiting Copilot Access

**Symptoms:** Users outside deployment group can access Copilot features, or users inside deployment group cannot access

**Resolution:**

1. **Verify group type:**
   - Deployment groups must be **Security groups** in Entra ID
   - Navigate to Microsoft Entra admin center > Groups > [Deployment Group]
   - Verify "Group type" is "Security"
   - If incorrect, recreate as security group and reassign members

2. **Check license assignment:**
   - Verify users have M365 Copilot licenses assigned
   - Deployment groups control availability, but licenses are still required
   - Navigate to M365 Admin Center > Users > Active users > [User] > Licenses
   - If license missing, assign M365 Copilot license

3. **Verify deployment group configuration:**
   - Navigate to M365 Admin Center > Copilot > Settings
   - Check if deployment group setting is enabled and pointing to correct group
   - Confirm group ID matches the intended deployment group

4. **Allow propagation time:**
   - Deployment group changes take up to **8 hours** to propagate
   - Check timestamp of configuration change
   - If less than 8 hours, wait for full propagation window
   - Test again after propagation window completes

5. **Check for Admin Exclusion Group conflicts:**
   - If user is in BOTH deployment group AND Admin Exclusion Group, exclusion takes precedence
   - Verify user is not inadvertently in exclusion group
   - Admin Exclusion Group overrides deployment group membership

**Diagnostic Commands:**
```powershell
# Verify user's deployment group membership
$deploymentGroup = Get-MgGroup -Filter "displayName eq 'Copilot-Pilot-IT-Compliance'"
$user = Get-MgUser -Filter "userPrincipalName eq 'user@contoso.com'"
Get-MgGroupMember -GroupId $deploymentGroup.Id | Where-Object { $_.Id -eq $user.Id }

# Check if user is in exclusion group
$exclusionGroup = Get-MgGroup -Filter "displayName eq 'CopilotForM365AdminExclude'"
Get-MgGroupMember -GroupId $exclusionGroup.Id | Where-Object { $_.Id -eq $user.Id }
```

---

#### Issue: Web Search Still Returning Results After Disabling

**Symptoms:** Copilot responses include web-grounded content despite web search being disabled in settings

**Resolution:**

1. **Allow propagation delay:**
   - Web search setting changes take up to **8 hours** to propagate across tenant
   - Check timestamp of when web search was disabled
   - If less than 8 hours, wait for full propagation window
   - Note: Propagation time can vary; some tenants may see faster updates

2. **Verify setting at correct scope:**
   - Navigate to M365 Admin Center > Copilot > Settings > Data access
   - Verify "Web search for M365 Copilot" is set to "Disabled"
   - Check if setting is applied at tenant level (not just group-level override)
   - Some organizations may have multiple scopes; ensure tenant-level setting is disabled

3. **Distinguish web search from organizational data:**
   - Copilot may still provide responses that APPEAR web-like but are from organizational data
   - Verify response sources — does Copilot cite external websites or only internal documents?
   - Test with query that clearly requires external web (e.g., "What happened in the news today?")
   - If response indicates "I don't have access to web data" but provides organizational info, setting is working correctly

4. **Check user-level overrides:**
   - Some Copilot implementations may have user-level or group-level web search overrides
   - Verify no Conditional Access policies or other settings re-enable web search for specific users
   - Test with multiple users in different groups to isolate scope issue

5. **Clear user session and cache:**
   - Have user sign out of all M365 sessions
   - Clear browser cache
   - Sign back in and test Copilot query
   - Cached responses may appear web-grounded even after setting disabled

**Diagnostic Steps:**
- Test query: "What are the latest news headlines?" (requires web)
- Expected response with web disabled: "I don't have access to web search" or similar message
- If Copilot provides news headlines, web search may still be enabled or propagation incomplete

---

### General Copilot Issues

#### Issue: Copilot Section Not Visible

**Symptoms:** Copilot not in M365 Admin Center navigation

**Resolution:**

1. Verify M365 Copilot licenses assigned in tenant
2. Ensure user has Entra Global Admin role
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

*Updated: January 2026 | Version: v1.2*
