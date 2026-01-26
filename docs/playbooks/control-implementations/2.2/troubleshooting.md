# Troubleshooting: Control 2.2 - Environment Groups and Tier Classification

**Last Updated:** January 2026

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| Rules not applying to environment | Environment not in group or rules not published | Verify group membership; publish rules |
| Cannot add environment to group | Environment not managed | Enable Managed Environment first ([Control 2.1](../../../controls/pillar-2-management/2.1-managed-environments.md)) |
| Rule conflicts | Group and environment settings conflict | More restrictive wins; document which takes precedence |
| Environment group not visible | Missing admin role or group deleted | Verify Power Platform Admin role; check if group exists |
| Published rules slow to apply | Normal propagation delay | Allow up to 15 minutes for propagation |
| External model rule not blocking | Rule not published or user exemption | Verify rule published; check for exemptions |

---

## Detailed Troubleshooting

### Issue: Rules Not Applying to Environment

**Symptoms:** Environment settings don't match group rules after configuration.

**Diagnostic Steps:**

1. Verify environment is in the group:
   ```
   PPAC > Environment groups > [Group] > Environments tab
   ```

2. Verify rules are published:
   ```
   PPAC > Environment groups > [Group] > Rules tab > Check "Published" status
   ```

3. Check environment is Managed:
   ```
   PPAC > Environments > [env] > Check Managed Environment status
   ```

4. Wait for propagation (up to 15 minutes)

**Resolution:**

- Add environment to group if missing
- Publish rules if not already published
- Enable Managed Environment if not managed
- Wait and re-check after 15 minutes

---

### Issue: Cannot Add Environment to Group

**Symptoms:** "Environment cannot be added" error or environment not selectable.

**Diagnostic Steps:**

1. Check if environment is a Managed Environment:
   ```
   PPAC > Environments > [env] > Check for "Managed" badge
   ```

2. Verify you have Environment Admin rights for the environment

3. Check if environment is in a locked/disabled state

**Resolution:**

- Enable Managed Environment first ([Control 2.1](../../../controls/pillar-2-management/2.1-managed-environments.md))
- Request Environment Admin role if missing
- Wait for pending operations to complete

---

### Issue: Rule Conflicts Between Group and Environment

**Symptoms:** Inconsistent behavior - some settings work, others don't.

**Diagnostic Steps:**

1. Review group-level rules:
   ```
   PPAC > Environment groups > [Group] > Rules
   ```

2. Review environment-level settings:
   ```
   PPAC > Environments > [env] > Settings/Features
   ```

3. Compare settings and identify conflicts

**Resolution:**

- Document which settings come from group vs. environment
- The more restrictive setting takes precedence
- For clarity, align both to the same values where possible
- Document any intentional differences

---

### Issue: Environment Group Not Visible

**Symptoms:** Group doesn't appear in PPAC Environment groups list.

**Diagnostic Steps:**

1. Verify you have Power Platform Admin role:
   ```
   M365 Admin Center > Users > [Your account] > Roles
   ```

2. Check if group was deleted by another admin

3. Verify tenant-level feature is enabled

**Resolution:**

- Request Power Platform Admin role if missing
- Check audit logs for group deletion events
- Contact Microsoft Support if feature appears unavailable

---

### Issue: Published Rules Taking Time to Apply

**Symptoms:** Settings not immediately effective after publishing.

**Diagnostic Steps:**

1. Check the published timestamp in Rules tab

2. Wait 15 minutes for propagation

3. Clear browser cache and refresh PPAC

**Resolution:**

- Allow up to 15 minutes for rule propagation
- Refresh the portal after waiting
- If still not applied after 30 minutes, contact support

---

### Issue: External Model Rule Not Blocking

**Symptoms:** External AI models still accessible despite rule being disabled.

**Diagnostic Steps:**

1. Verify rule is published:
   ```
   PPAC > Environment groups > [Group] > Rules > Enable External Models
   ```

2. Check if user has any exemptions or elevated permissions

3. Confirm environment is in the correct group

**Resolution:**

- Publish the rule if not published
- Review user permissions for exemptions
- Verify environment group membership
- Wait for propagation if recently changed

---

### Issue: Maker Routed to Wrong Environment

**Symptoms:** New makers land in environments with incorrect tier rules.

**Diagnostic Steps:**

1. Review routing policy configuration:
   ```
   PPAC > Environments > Environment routing
   ```

2. Verify target environment is in the correct tier group

3. Check routing exceptions list

**Resolution:**

- Update routing policy targets ([Control 2.15](../../../controls/pillar-2-management/2.15-environment-routing.md))
- Ensure target environments are in appropriate tier groups
- Review and update exceptions if needed
- Re-test routing after changes

---

### Issue: Tier Intent Unclear During Audit

**Symptoms:** Group names/descriptions don't clearly indicate Tier 1/2/3 purpose.

**Diagnostic Steps:**

1. Review group descriptions for tier classification

2. Check if tier information is documented elsewhere

**Resolution:**

- Update group descriptions to include:
  - Tier classification (Tier 1, 2, or 3)
  - Allowed data scope
  - Change authority
- Regenerate exports and capture updated screenshots
- Document mapping in separate governance documentation

---

## How to Confirm Configuration is Active

### Via Portal

1. Navigate to **PPAC** > **Environment groups** > select group
2. Verify **Environments** tab shows expected membership
3. Verify **Rules** tab shows Published status with recent date
4. Open an environment in the group and verify settings match rules

### Via PowerShell

```powershell
# Quick validation check
$groupId = "<EnvironmentGroup-ID>"

# List environments in the group and confirm managed state
Get-AdminPowerAppEnvironment |
    Where-Object { $_.EnvironmentGroupId -eq $groupId } |
    Select-Object DisplayName, EnvironmentName, EnvironmentGroupId,
        @{Name='IsManaged'; Expression = {
            $_.Properties.governanceConfiguration.protectionLevel -ne 'Standard'
        }} |
    Format-Table -AutoSize
```

### Via Testing

1. Add a test environment to a group
2. Verify it inherits rules (e.g., try to share an agent in Tier 1)
3. Confirm expected blocking/allowing behavior

---

## Escalation Path

If issues persist after troubleshooting:

1. **Power Platform Admin Team** - Group and rule configuration issues
2. **IT Governance** - Tier classification and policy questions
3. **Microsoft Support** - Platform bugs or feature issues
4. **AI Governance Lead** - Agent-specific rule interpretation

### Microsoft Support Contact

For Environment Groups issues:

1. PPAC > **Help + support** > **New support request**
2. Select **Environment groups** as the issue category
3. Provide:
   - Environment Group ID
   - Detailed issue description
   - Steps to reproduce
   - Screenshots of configuration and error

---

## Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| Group creation via portal only | Cannot automate group creation | Use portal for initial setup; automate membership via PowerShell |
| Rule propagation delay | Up to 15 minutes for changes | Plan configuration changes during maintenance windows |
| No rule version history | Cannot rollback rules | Maintain manual documentation of rule changes |
| 21 rules (some in preview) | Feature availability may change | Document which features are GA vs. preview |
| Single group per environment | Cannot inherit from multiple groups | Use most restrictive group; supplement with environment-level settings |

---

## Security Warning: Computer-Using Agents (CUA)

If CUA-related issues arise:

**DO NOT enable CUA** to troubleshoot other issues. CUA poses significant security risks for FSI environments.

If you believe CUA was accidentally enabled:

1. Immediately verify CUA rule status for all groups
2. Set **Computer Use** rule to **Disabled** for all groups
3. Publish rules immediately
4. Document the incident per your security incident procedures
5. Review audit logs for any CUA activity during the exposure window

---

[Back to Control 2.2](../../../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
