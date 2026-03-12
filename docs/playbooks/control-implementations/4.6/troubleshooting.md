# Control 4.6: Grounding Scope Governance - Troubleshooting

> This playbook provides troubleshooting guidance for [Control 4.6](../../../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md).

---

## Common Issues and Solutions

### Issue: Content Still Appearing After Exclusion

**Symptoms:** Copilot returns content from site with RCD enabled

**Resolution:**

1. Verify exclusion setting is applied:
   ```powershell
   Get-SPOSite -Identity "https://contoso.sharepoint.com/sites/SiteName" |
       Select-Object Url, RestrictContentOrgWideSearch
   ```
2. Allow up to 24 hours for index to update
3. Check if content exists in multiple locations (may exist elsewhere)
4. Verify user doesn't have direct access bypassing exclusion
5. Contact Microsoft support if issue persists after 48 hours

---

### Issue: Cannot Set Site Exclusion Property

**Symptoms:** Set-SPOSite fails with permission error

**Resolution:**

1. Verify SharePoint Admin role assignment
2. Check SharePoint Advanced Management license
3. Ensure site isn't locked or read-only
4. Try via SharePoint Admin Center UI as alternative
5. Verify tenant-level settings allow modification

---

### Issue: CopilotReady Property Not Persisting

**Symptoms:** Property bag values not saving

**Resolution:**

1. Verify PnP.PowerShell module is current version:
   ```powershell
   Update-Module -Name PnP.PowerShell
   ```
2. Check site collection admin permissions
3. Ensure property bag is not read-only
4. Use Connect-PnPOnline with appropriate authentication
5. Verify site isn't in read-only or archive state

---

### Issue: Copilot Still Returning Content from Non-Allowed Sites After Enabling Restricted Search

**Symptoms:** Restricted Search is enabled, but Copilot returns content from sites not in the allowed list

**Resolution:**

1. **Verify Restricted Search is enabled at tenant level:**
   ```powershell
   Get-SPOTenant | Select-Object EnableRestrictedSearchAllList
   ```
   Expected: `EnableRestrictedSearchAllList: True`

2. **Allow propagation delay (24-48 hours):**
   - Configuration changes can take up to 48 hours to fully propagate to Copilot grounding systems
   - Note the time you enabled Restricted Search
   - Wait full 48 hours before escalating

3. **Verify the site is NOT in the allowed list:**
   ```powershell
   Get-SPOTenantRestrictedSearchAllowedList | Where-Object { $_ -like "*SiteName*" }
   ```
   If site appears in results, it IS allowed (remove if unintended)

4. **Check for content duplication:**
   - Content may exist on multiple sites
   - Copilot may be grounding on an allowed site with duplicated content
   - Verify content source in Copilot citations

5. **Verify user interaction history:**
   - Users who recently interacted with content may still see it in recent files
   - Copilot may surface content from user's recent activity, which is separate from grounding

6. **Contact Microsoft support** if issue persists after 48 hours and above checks confirm configuration

---

### Issue: Unable to Add Site to Allowed List (100 Site Limit Reached)

**Symptoms:** `Add-SPOTenantRestrictedSearchAllowedList` fails with "limit exceeded" or similar error

**Resolution:**

1. **Verify current allowed list count:**
   ```powershell
   $count = (Get-SPOTenantRestrictedSearchAllowedList).Count
   Write-Host "Current allowed sites: $count / 100"
   ```

2. **Review and prioritize sites:**
   - Export current allowed list with usage metrics
   - Identify low-usage or outdated sites for removal
   - Document business case for new site vs. existing sites

3. **Remove low-priority sites:**
   ```powershell
   # After governance approval
   Remove-SPOTenantRestrictedSearchAllowedList -SiteUrl "https://contoso.sharepoint.com/sites/LowPriority"
   ```

4. **Consider using RCD for complementary exclusions:**
   - Restricted Search defines what IS allowed (positive)
   - RCD can exclude specific content WITHIN allowed sites (negative)
   - Use both approaches together for fine-grained control

5. **Consolidate content where possible:**
   - Merge low-usage sites into existing allowed sites
   - Reduces site count while preserving content

---

### Issue: Restricted Search Enabled But Copilot Returns No Results

**Symptoms:** After enabling Restricted Search, Copilot cannot answer any queries, even for allowed sites

**Resolution:**

1. **Verify at least one site is in the allowed list:**
   ```powershell
   Get-SPOTenantRestrictedSearchAllowedList
   ```
   If empty, add approved sites

2. **Verify user has permissions to allowed sites:**
   - Restricted Search does NOT override SharePoint permissions
   - User must have access to allowed sites to see grounded content
   - Check user's site permissions

3. **Check SharePoint search index health:**
   ```powershell
   # Verify sites are indexed
   Get-SPOSite -Identity "https://contoso.sharepoint.com/sites/AllowedSite" |
       Select-Object Url, LastContentModifiedDate
   ```
   If LastContentModifiedDate is very old, content may be stale

4. **Verify propagation delay:**
   - Allow 24-48 hours after adding sites to allowed list
   - Test with known content from allowed sites

5. **Check for conflicting RCD settings:**
   - If a site is in the allowed list BUT has RCD enabled, RCD takes precedence
   - Verify: `Get-SPOSite -Identity $siteUrl | Select-Object RestrictContentOrgWideSearch`
   - Should be `False` for allowed sites

---

## Diagnostic Commands

```powershell
# Check site exclusion status
Get-SPOSite -Identity "https://contoso.sharepoint.com/sites/SiteName" |
    Select-Object Url, RestrictContentOrgWideSearch, LockState

# Verify property bag access
Connect-PnPOnline -Url "https://contoso.sharepoint.com/sites/SiteName" -Interactive
Get-PnPPropertyBag | Where-Object { $_.Key -like "Copilot*" }

# Check for sites with inconsistent state
Get-SPOSite -Limit All | Where-Object {
    $_.RestrictContentOrgWideSearch -eq $null
} | Select-Object Url
```

---

## Escalation Path

| Issue Severity | Escalation Path | SLA |
|---------------|-----------------|-----|
| Exclusion not applying after 48 hours | SharePoint Admin > Microsoft Support | 2 business days |
| Content surfacing from excluded site | AI Governance Lead > Security > Microsoft Support | Same day |
| Property bag issues | SharePoint Admin > PnP Community | 1 business day |
| Bulk exclusion failures | SharePoint Admin > Microsoft Support | 2 business days |

---

## Prevention Best Practices

1. **Document all exclusion decisions** with business justification
2. **Test exclusions in non-production** before applying to critical sites
3. **Verify exclusions weekly** for the first month
4. **Establish approval workflow** for grounding scope changes
5. **Monitor audit logs** for unauthorized scope modifications
6. **Schedule quarterly reviews** of grounding scope policy

---

## Related Resources

- [Microsoft 365 Copilot data, privacy, and security](https://learn.microsoft.com/en-us/copilot/microsoft-365/microsoft-365-copilot-privacy)
- [Restrict Discovery of SharePoint Sites and Content](https://learn.microsoft.com/en-us/sharepoint/restricted-content-discovery)
- [SharePoint Advanced Management overview](https://learn.microsoft.com/en-us/sharepoint/advanced-management)

---

[Back to Control 4.6](../../../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)

---

*Updated: January 2026 | Version: v1.2*
