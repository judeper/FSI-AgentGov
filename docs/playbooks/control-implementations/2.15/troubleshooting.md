# Troubleshooting: Control 2.15 - Environment Routing and Auto-Provisioning

**Last Updated:** January 2026

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| User not routed to expected environment | Rule not matching or lower priority | Check rule conditions and priority order |
| All users going to default environment | Rules not active or conditions too strict | Verify rules are enabled and conditions are achievable |
| Routing not working at all | Environment groups not configured | Verify group exists with environments and rules |
| User can see multiple environments | Routing doesn't restrict, only defaults | By design - routing sets default, doesn't hide environments |
| Rules not saving | Permission or validation error | Check admin permissions; verify rule syntax |

---

## Detailed Troubleshooting

### Issue: User Not Routed to Expected Environment

**Symptoms:** User sees different environment than expected based on rules

**Diagnostic Steps:**

1. Verify user's group membership:
   ```
   Microsoft Entra Admin Center > Users > [User] > Groups
   ```

2. Check rule conditions in PPAC:
   ```
   PPAC > Environments > Environment groups > [Group] > Rules
   ```

3. Verify rule priority - lower number = higher priority

4. Check if user matches a higher-priority rule

**Resolution:**

- Add user to correct security group if missing
- Adjust rule conditions to be less restrictive
- Reorder rule priorities if needed
- Wait for group membership sync (up to 24 hours)

---

### Issue: All Users Going to Default Environment

**Symptoms:** No routing rules seem to take effect

**Diagnostic Steps:**

1. Verify environment group has environments:
   ```
   PPAC > Environments > Environment groups > [Group] > Environments tab
   ```

2. Check that rules exist and are not empty:
   ```
   PPAC > Environments > Environment groups > [Group] > Rules tab
   ```

3. Verify rule conditions are achievable:
   - Security group exists and has members
   - Domain pattern matches user emails
   - Geographic conditions match user locations

4. Test with a user you're certain matches a rule

**Resolution:**

- Add environments to the group if empty
- Create routing rules if none exist
- Fix rule conditions to match actual user attributes
- Verify security groups exist in Azure AD

---

### Issue: Users Can See Multiple Environments

**Symptoms:** Users expected to be restricted can still select other environments

**Diagnostic Steps:**

1. Understand routing behavior:
   - Routing sets the **default** environment, not access restrictions
   - Users may still have access to other environments

2. Check environment security:
   ```
   PPAC > Environments > [env] > Settings > Users + permissions
   ```

3. Verify if this is expected behavior or a misconfiguration

**Resolution:**

- Routing only affects default selection
- Use environment security roles to restrict access
- Remove users from environments they shouldn't access
- Combine routing with security role management

---

### Issue: Rules Not Saving

**Symptoms:** Changes to routing rules are lost or error on save

**Diagnostic Steps:**

1. Verify admin permissions:
   - Requires Power Platform Administrator role

2. Check rule syntax:
   - Security group must be valid Azure AD group
   - Domain patterns must be valid

3. Check for validation errors in the UI

4. Try saving with minimal changes

**Resolution:**

- Verify Power Platform Administrator role is assigned
- Correct any invalid rule conditions
- Try creating a new simple rule to test
- Contact Microsoft Support if persists

---

## How to Confirm Configuration is Active

### Via Portal

1. Navigate to **PPAC** > **Environments** > **Environment groups**
2. Verify groups have environments listed
3. Open **Rules** tab and confirm rules exist
4. Test with a user matching rule conditions

### Via User Experience

1. Sign in as a user matching a routing rule
2. Go to Power Apps or Copilot Studio
3. Click **+ Create**
4. Verify the correct environment is pre-selected

---

## Escalation Path

If issues persist after troubleshooting:

1. **Power Platform Admin Team** - Environment and routing configuration
2. **Identity Team** - Security group membership issues
3. **Microsoft Support** - Platform bugs or limitations
4. **AI Governance Lead** - Policy questions

---

## Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| Routing sets default only | Users may still access other environments | Use security roles to restrict access |
| Group membership sync delay | New members may not route immediately | Wait 24 hours; verify group membership |
| Limited rule condition types | Cannot route on all attributes | Use security groups as proxy for complex conditions |
| No "deny" routing option | Cannot block users from all environments | Remove environment access via security roles |
| Rule evaluation at session start | Changes don't affect active sessions | Users must log out and back in |

---

[Back to Control 2.15](../../../controls/pillar-2-management/2.15-environment-routing.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
