# Control 4.6: Grounding Scope Governance - Troubleshooting

> This playbook provides troubleshooting guidance for [Control 4.6](../../../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md).

---

## Common Issues and Solutions

### Issue: Content Still Appearing After Exclusion

**Symptoms:** Copilot returns content from site with RCD enabled

**Resolution:**

1. Verify exclusion setting is applied:
   ```powershell
   Get-SPOSite -Identity "https://tenant.sharepoint.com/sites/SiteName" |
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

## Diagnostic Commands

```powershell
# Check site exclusion status
Get-SPOSite -Identity "https://tenant.sharepoint.com/sites/SiteName" |
    Select-Object Url, RestrictContentOrgWideSearch, LockState

# Verify property bag access
Connect-PnPOnline -Url "https://tenant.sharepoint.com/sites/SiteName" -Interactive
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

- [Microsoft 365 Copilot data, privacy, and security](https://learn.microsoft.com/en-us/microsoft-365-copilot/microsoft-365-copilot-privacy)
- [Restrict Discovery of SharePoint Sites and Content](https://learn.microsoft.com/en-us/sharepoint/restricted-content-discovery)
- [SharePoint Advanced Management overview](https://learn.microsoft.com/en-us/sharepoint/advanced-management)

---

*Updated: January 2026 | Version: v1.2*
