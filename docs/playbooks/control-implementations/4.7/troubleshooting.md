# Control 4.7: Microsoft 365 Copilot Data Governance - Troubleshooting

> This playbook provides troubleshooting guidance for [Control 4.7](../../../controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md).

---

## Common Issues and Solutions

### Issue: Copilot Returning Content from Excluded Site

**Symptoms:** User sees content from site with RCD enabled

**Resolution:**

1. Verify RCD setting on the site:
   ```powershell
   Get-SPOSite -Identity "https://tenant.sharepoint.com/sites/SiteName" |
       Select-Object Url, RestrictContentOrgWideSearch
   ```
2. Allow 24 hours for index propagation
3. Check if content exists in multiple locations
4. Verify user doesn't have direct access bypassing RCD
5. Contact Microsoft support if persistent

---

### Issue: Plugin Not Available After Approval

**Symptoms:** Approved plugin not appearing for users

**Resolution:**

1. Verify plugin is enabled in Admin Center
2. Check user has required license
3. Verify plugin assignment (all users vs. specific groups)
4. Clear browser cache and retry
5. Check for Conditional Access policies blocking plugin

---

### Issue: Usage Analytics Not Showing Data

**Symptoms:** Copilot usage reports empty or incomplete

**Resolution:**

1. Verify users have M365 Copilot licenses
2. Allow 48-72 hours for data population
3. Check reporting permissions for admin account
4. Verify no data export restrictions
5. Review Microsoft 365 service health

---

### Issue: Sensitivity Labels Not Respected

**Symptoms:** Copilot surfaces content despite sensitivity labels

**Resolution:**

1. Verify label includes Copilot restrictions
2. Check label policy assignment to users
3. Verify label is applied to content (not just site)
4. Review DLP policy enforcement
5. Contact Purview support if needed

---

## Diagnostic Commands

```powershell
# Check site exclusion status
Get-SPOSite -Identity "https://tenant.sharepoint.com/sites/SiteName" |
    Select-Object Url, RestrictContentOrgWideSearch, SensitivityLabel

# Verify Graph Connector status
Get-MgExternalConnection | ForEach-Object {
    Write-Host "$($_.Name): $($_.State)"
}

# Count excluded vs included sites
$sites = Get-SPOSite -Limit All | Where-Object { $_.Template -notlike "*SPSPERS*" }
$excluded = ($sites | Where-Object { $_.RestrictContentOrgWideSearch -eq $true }).Count
$included = ($sites | Where-Object { $_.RestrictContentOrgWideSearch -ne $true }).Count
Write-Host "Excluded: $excluded | Included: $included"
```

---

## Escalation Path

| Issue Severity | Escalation Path | SLA |
|---------------|-----------------|-----|
| Content surfacing from excluded site | AI Governance Lead > Security > Microsoft Support | Same day |
| Plugin access issues | IT Admin > Microsoft Support | 2 business days |
| Usage analytics gaps | M365 Admin > Microsoft Support | 2 business days |
| Sensitivity label issues | Purview Admin > Microsoft Support | 1 business day |

---

## Prevention Best Practices

1. **Document all exclusion decisions** with business justification
2. **Test exclusions** before announcing Copilot availability
3. **Publish acceptable use policy** before rollout
4. **Train users** on appropriate use and limitations
5. **Monitor usage patterns** for anomalies
6. **Review plugin inventory** quarterly
7. **Establish output review processes** before enabling for external communications

---

## Related Resources

- [Microsoft 365 Copilot overview](https://learn.microsoft.com/en-us/microsoft-365-copilot/microsoft-365-copilot-overview)
- [Microsoft 365 Copilot data, privacy, and security](https://learn.microsoft.com/en-us/microsoft-365-copilot/microsoft-365-copilot-privacy)
- [Manage Microsoft 365 Copilot](https://learn.microsoft.com/en-us/microsoft-365-copilot/microsoft-365-copilot-enable-users)
- [Restricted Content Discovery](https://learn.microsoft.com/en-us/sharepoint/restricted-content-discovery)

---

*Updated: January 2026 | Version: v1.1*
