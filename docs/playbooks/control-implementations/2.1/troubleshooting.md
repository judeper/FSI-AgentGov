# Troubleshooting: Control 2.1 - Managed Environments

**Last Updated:** January 2026

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| Cannot enable Managed Environment | Missing admin role or pending operations | Verify Power Platform Admin role; check for pending environment operations |
| Solution checker blocking valid solutions | False positives or strict rules | Review findings; use Warn mode while addressing; create documented exceptions |
| Usage insights not arriving | Email config or empty environment | Verify recipients; check spam; wait one week; confirm environment has activity |
| Sharing limits not enforcing | Settings not saved or admin bypass | Reopen panel to verify; check if user is admin (admins bypass limits) |
| Maker welcome content not displaying | First-time flag or popup blocker | Test with new user; check browser popup settings |
| Settings propagation delay | Normal sync latency | Wait up to 1 hour for settings to take effect |

---

## Detailed Troubleshooting

### Issue: Cannot Enable Managed Environment

**Symptoms:** Managed Environment option not available or fails to enable

**Diagnostic Steps:**

1. Verify you have Power Platform Admin role:
   ```
   Microsoft 365 Admin Center > Users > [Your account] > Roles
   ```

2. Check environment state:
   ```
   PPAC > Environments > [env] > Check for pending operations or locked state
   ```

3. Verify Dataverse capacity (if enabling features that require it):
   ```
   PPAC > Resources > Capacity
   ```

4. Check for in-progress environment operations:
   ```
   PPAC > Environments > [env] > Activity log
   ```

**Resolution:**

- Assign Power Platform Admin role if missing
- Wait for pending operations to complete
- Add Dataverse capacity if needed for specific features
- Contact Microsoft Support if environment is locked

---

### Issue: Solution Checker Blocking Valid Solutions

**Symptoms:** Legitimate solutions blocked on import due to checker findings

**Diagnostic Steps:**

1. Review the specific solution checker findings:
   ```
   PPAC > Environments > [env] > Solution checker results
   ```

2. Check severity levels of findings (Critical, High, Medium, Low)

3. Verify if findings are false positives or legitimate issues

**Resolution:**

1. Address Critical and High severity items before import
2. For false positives:
   - Document the false positive with justification
   - Create an exception record in your GRC system
   - Consider excluding specific rules (use cautiously)
3. Temporarily switch to "Warn" mode while addressing issues
4. Contact Microsoft Support for persistent false positives

**Best Practice:** Maintain a log of all solution checker exceptions with:
- Solution name and version
- Finding details
- Justification for exception
- Approver and date

---

### Issue: Usage Insights Not Arriving

**Symptoms:** Weekly usage digest emails not received

**Diagnostic Steps:**

1. Verify email addresses are correctly configured:
   ```
   PPAC > Environments > [env] > Edit managed environments > Usage insights
   ```

2. Check spam/junk folders for digest emails from Microsoft

3. Confirm environment has active usage:
   - Apps being run
   - Flows executing
   - Agents being used

4. Check the timing - digests are sent weekly on Mondays

**Resolution:**

- Correct email addresses in configuration
- Add Microsoft sender addresses to safe senders list
- Wait for next weekly cycle
- If environment is new/empty, generate test activity first
- Verify environment is still marked as Managed

---

### Issue: Sharing Limits Not Enforcing

**Symptoms:** Users can share apps/agents beyond configured limits

**Diagnostic Steps:**

1. Verify settings were saved:
   ```
   PPAC > Environments > [env] > Edit managed environments
   Reopen panel and confirm limits are still configured
   ```

2. Check if the sharing user is an Environment Admin:
   ```
   PPAC > Environments > [env] > Settings > Users + permissions
   ```

3. Verify limits are set for the correct resource type (Apps/Flows/Agents)

4. Check for conflicting environment group rules

**Resolution:**

- Save settings again if not persisted
- Note that Environment Admins and Dataverse System Admins bypass sharing limits
- Verify limits for correct resource type
- Check environment group rules (more restrictive wins)
- Wait up to 1 hour for propagation

---

### Issue: Maker Welcome Content Not Displaying

**Symptoms:** Makers don't see welcome content on environment access

**Diagnostic Steps:**

1. Verify content was saved:
   ```
   PPAC > Environments > [env] > Edit managed environments > Maker welcome content
   Use "See preview" to confirm content exists
   ```

2. Check if maker has accessed environment before (only shows on first access)

3. Test with different browser/incognito mode

4. Check browser popup blocker settings

**Resolution:**

- Re-save maker welcome content if not showing
- Test with a new user account (never accessed environment)
- Disable popup blocker for Power Apps/Copilot Studio URLs
- Verify environment is correctly marked as Managed

---

### Issue: Cross-Tenant Restrictions Not Working

**Symptoms:** Users can still access external tenant resources

**Diagnostic Steps:**

1. Verify cross-tenant settings:
   ```
   PPAC > Environments > [env] > Settings > Product > Privacy + Security
   ```

2. Check if the connector being used is subject to cross-tenant restrictions

3. Verify the connection was created after restrictions were enabled

**Resolution:**

- Re-configure cross-tenant settings
- Delete and recreate connections created before restrictions
- Some connectors may not support cross-tenant restrictions
- Contact Microsoft Support for connector-specific guidance

---

## How to Confirm Configuration is Active

### Via Portal

1. Navigate to **PPAC** > **Environments** > select environment
2. Verify **Managed environments** card shows enabled
3. Open **Edit managed environments** to verify all settings

### Via PowerShell

```powershell
# Quick validation check
$EnvironmentName = "your-environment-id"

$env = Get-AdminPowerAppEnvironment -EnvironmentName $EnvironmentName

Write-Host "Environment: $($env.DisplayName)" -ForegroundColor Cyan
Write-Host "Managed: $(if ($env.Properties.protectionLevel -ne 'Standard') { 'Yes' } else { 'No' })"
Write-Host "Type: $($env.EnvironmentType)"
Write-Host "Region: $($env.Location)"
Write-Host "State: $($env.States.Runtime)"
```

### Via User Testing

1. Have a non-admin maker attempt to share beyond limits
2. Verify sharing is blocked
3. Have a new user access environment and verify welcome content displays

---

## Escalation Path

If issues persist after troubleshooting:

1. **Power Platform Admin Team** - Environment configuration issues
2. **IT Governance** - Policy and compliance questions
3. **Microsoft Support** - Platform bugs or feature issues
4. **AI Governance Lead** - Agent-specific settings questions

### Microsoft Support Contact

For Managed Environment issues:
1. PPAC > **Help + support** > **New support request**
2. Select **Environment** as the issue category
3. Provide:
   - Environment ID
   - Detailed issue description
   - Steps to reproduce
   - Screenshots of error/behavior

---

## Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| Admins bypass sharing limits | Admins can share without restrictions | Limit admin role assignments; document admin shares separately |
| Usage insights weekly only | No real-time usage data | Use audit logs for immediate visibility |
| Solution checker requires Dataverse | Cannot use checker in non-Dataverse environments | Rely on DLP and sharing limits; document N/A status |
| Welcome content 1500 char limit | Limited space for policy content | Link to full policy document; keep content concise |
| Settings propagation delay | Up to 1 hour for changes | Plan configuration during maintenance windows |

---

[Back to Control 2.1](../../../controls/pillar-2-management/2.1-managed-environments.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
