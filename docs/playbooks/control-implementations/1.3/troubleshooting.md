# Troubleshooting: Control 1.3 - SharePoint Content Governance and Permissions

**Last Updated:** January 2026

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| Agent cannot access required content | Service account not in site members | Add service account to site members group |
| Agent accessing content it shouldn't | Broad permissions or inheritance | Review knowledge source config; remove "Everyone" groups |
| Sensitivity labels not appearing | Labels not published to users | Verify label publication in Purview |
| External sharing still possible | Site-level override | Check site vs. tenant settings; site cannot be more permissive |
| Access review not sending notifications | Configuration issue | Verify reviewer assignments and email settings |
| IAG not blocking content discovery | Policy not applied | Check IAG policy scope and site inclusion |

---

## Detailed Troubleshooting

### Issue: Agent Cannot Access Required Content

**Symptoms:** Agent returns "I don't have access to that information" for valid content

**Diagnostic Steps:**

1. Verify agent service account is in site members group:
   ```powershell
   $SiteUrl = "https://contoso.sharepoint.com/sites/Agent-CustomerService"
   Get-SPOUser -Site $SiteUrl -LoginName "agent-service@contoso.com"
   ```

2. Check sensitivity label on content matches agent's allowed labels

3. Confirm IAG/restricted content discoverability isn't blocking:
   - SharePoint Admin Center > Sites > [site] > Policies > Restricted access control

4. Review Conditional Access policies that might block service account

5. Check if site requires MFA and service account can satisfy

**Resolution:**
- Add service account to appropriate site group
- Verify service account is excluded from blocking Conditional Access policies
- Check label-based access policies in Purview

---

### Issue: Agent Accessing Content It Shouldn't

**Symptoms:** Agent returning sensitive information from excluded sites

**Diagnostic Steps:**

1. Review agent knowledge source configuration in Copilot Studio:
   - Check which sites/libraries are configured as knowledge sources

2. Verify site permissions don't include broad groups:
   ```powershell
   $Users = Get-SPOUser -Site $SiteUrl -Limit All
   $Users | Where-Object { $_.LoginName -match "everyone" }
   ```

3. Check for inheritance from parent site

4. Review agent service account's total permissions across tenant

**Resolution:**
- Remove broad "Everyone" or "All Users" permissions
- Configure explicit knowledge sources in Copilot Studio
- Break permission inheritance if needed

---

### Issue: Sensitivity Labels Not Appearing on Documents

**Symptoms:** Documents don't show expected sensitivity labels

**Diagnostic Steps:**

1. Verify labels are published to users in the site:
   - Purview > Information Protection > Label policies
   - Check policy scope includes site users

2. Check if auto-labeling policies are configured

3. Confirm user has Information Protection client installed (for Office apps)

4. Review if default library label is configured:
   - Library settings > Apply sensitivity label to items

**Resolution:**
- Publish labels to appropriate users/groups
- Configure default library label for automatic application
- For existing documents, run retroactive labeling

---

### Issue: External Sharing Still Possible Despite Settings

**Symptoms:** Users can share externally from restricted sites

**Diagnostic Steps:**

1. Check site-level override vs. tenant settings:
   ```powershell
   # Site setting
   (Get-SPOSite -Identity $SiteUrl).SharingCapability

   # Tenant setting
   (Get-SPOTenant).SharingCapability
   ```
   Note: Site cannot be more permissive than tenant

2. Verify setting saved correctly (refresh admin center)

3. Check for PowerShell scripts that may be resetting values

4. Confirm user isn't a site collection admin (different permissions)

**Resolution:**
- Set site sharing to "Disabled" or more restrictive
- Verify tenant-level settings are appropriately restrictive
- Remove site collection admin rights from non-admin users

---

### Issue: Access Review Not Working

**Symptoms:** Access reviews not sending notifications or not completing

**Diagnostic Steps:**

1. Verify access review is configured correctly:
   - Entra Admin Center > Identity Governance > Access Reviews

2. Check reviewer assignments are valid

3. Verify email notifications are enabled

4. Check if reviewers have required permissions

**Resolution:**
- Reconfigure access review with correct settings
- Ensure reviewers have mailboxes and are not blocked
- Consider using backup reviewers

---

## How to Confirm Configuration is Active

### Via Portal (SharePoint Admin Center)

1. Navigate to **Policies** > **Sharing**
2. Verify tenant-level settings match FSI requirements
3. Navigate to **Sites** > **Active sites** > Select site
4. Verify site-level sharing is restricted

### Via Portal (Site Level)

1. Navigate to the SharePoint site
2. Go to **Site settings** > **Site permissions**
3. Verify no "Everyone" groups
4. Check all permission grants are documented

### Via PowerShell

```powershell
# Quick validation check
Write-Host "=== SharePoint Governance Check ===" -ForegroundColor Cyan

# Check tenant settings
$Tenant = Get-SPOTenant
Write-Host "Tenant Sharing: $($Tenant.SharingCapability)"

# Check specific site
$SiteUrl = "https://contoso.sharepoint.com/sites/Agent-CustomerService"
$Site = Get-SPOSite -Identity $SiteUrl

Write-Host "`nSite: $SiteUrl"
Write-Host "  Sharing: $($Site.SharingCapability)"
Write-Host "  Sensitivity: $($Site.SensitivityLabel)"
Write-Host "  Lock State: $($Site.LockState)"

# Check for broad permissions
$Users = Get-SPOUser -Site $SiteUrl -Limit All
$BroadAccess = $Users | Where-Object { $_.LoginName -match "everyone|spo-grid-all-users" }

if ($BroadAccess) {
    Write-Host "`n[WARN] Found broad permissions:" -ForegroundColor Yellow
    $BroadAccess | Format-Table DisplayName, LoginName
} else {
    Write-Host "`n[PASS] No broad 'Everyone' permissions" -ForegroundColor Green
}
```

---

## Escalation Path

If issues persist after troubleshooting:

1. **SharePoint Administrator** - Site configuration and permissions
2. **Information Protection Team** - Sensitivity labels and DLP
3. **Compliance Officer** - Regulatory requirements and evidence
4. **AI Governance Lead** - Agent data source approval
5. **Microsoft Support** - Platform bugs or feature issues

---

[Back to Control 1.3](../../../controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
