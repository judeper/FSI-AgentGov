# Troubleshooting: Control 4.1 - SharePoint Information Access Governance (IAG)

**Last Updated:** January 2026

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| Content restriction not working | Setting not propagated or cached | Wait 24-48 hours for propagation; clear Copilot cache; verify setting via PowerShell |
| Cannot enable restriction | Missing SharePoint Advanced Management license | Verify SAM license is assigned to tenant; contact Microsoft support |
| Audit logs missing | Unified Audit Log not enabled | Enable Unified Audit Log in Purview compliance portal |
| PowerShell connection fails | Expired credentials or MFA required | Use modern authentication; ensure admin account has MFA configured |
| Bulk update failures | Insufficient permissions or site-level overrides | Verify Site Collection Admin rights; check for site-level policies |

---

## Detailed Troubleshooting

### Issue: Copilot Still Returns Content from Restricted Sites

**Symptoms:** After enabling RCD, Microsoft 365 Copilot still surfaces content from the restricted site.

**Diagnostic Steps:**

1. Verify the restriction is applied via PowerShell:
   ```powershell
   Get-SPOSite -Identity "https://yourtenant.sharepoint.com/sites/SiteName" |
       Select-Object Url, RestrictContentOrgWideSearch
   ```

2. Check if the setting shows `RestrictContentOrgWideSearch = True`

3. If setting is correct but content still appears:
   - Allow up to 24-48 hours for the semantic index to update
   - Verify the content doesn't exist in other unrestricted locations
   - Check if user has direct access that bypasses restrictions

**Resolution:**
- Wait for index propagation (up to 48 hours)
- Search for duplicate content in other locations
- Contact Microsoft support if issue persists after 72 hours

---

### Issue: Cannot Enable Copilot Content Restriction

**Symptoms:** The "Restrict content from Microsoft 365 Copilot" option is grayed out or not visible.

**Diagnostic Steps:**

1. Verify SharePoint Advanced Management license:
   ```powershell
   Get-SPOTenant | Select-Object EnableAIPIntegration, AIBuilderEnabled
   ```

2. Check your admin role assignment (must be SharePoint Admin or Entra Global Admin)

3. Verify you're accessing SharePoint Admin Center (not classic site settings)

**Resolution:**
- Confirm SharePoint Advanced Management Plan 1 license is assigned to the tenant
- Ensure you have the correct admin role
- Use the modern SharePoint Admin Center (admin.sharepoint.com)
- Contact Microsoft support if license is confirmed but feature unavailable

---

### Issue: Restricted Access Control (RAC) Not Blocking Users

**Symptoms:** Users outside the authorized security group can still access RAC-protected sites.

**Diagnostic Steps:**

1. Verify RAC is enabled on the site:
   ```powershell
   Get-SPOSite -Identity $SiteUrl | Select-Object Url, RestrictedAccessControl, RestrictedAccessControlGroups
   ```

2. Verify the security group IDs are correct:
   ```powershell
   # Get Entra ID group details
   Connect-MgGraph -Scopes "Group.Read.All"
   Get-MgGroup -Filter "displayName eq 'GroupName'" | Select-Object Id, DisplayName
   ```

3. Check if user is a site owner (owners retain access regardless of RAC)

**Resolution:**
- Confirm the correct Entra ID group GUIDs are used
- Note that site owners always retain access
- Verify group membership is current
- Allow 15-60 minutes for group membership sync

---

### Issue: Audit Logs Not Showing IAG Changes

**Symptoms:** Configuration changes not appearing in Microsoft Purview Audit.

**Diagnostic Steps:**

1. Verify Unified Audit Log is enabled:
   ```powershell
   Connect-IPPSSession
   Get-AdminAuditLogConfig | Select-Object UnifiedAuditLogIngestionEnabled
   ```

2. Verify you're searching the correct date range (events may have 24-48 hour delay)

3. Use the correct search criteria:
   - Activity: "SiteRestrictedFromOrgSearch"
   - Record type: "SharePoint"

**Resolution:**
- Enable Unified Audit Log if disabled
- Expand search date range
- Wait 24-48 hours for new events to appear
- Verify search permissions (Purview Compliance Admin or equivalent)

---

### Issue: RSS (Restricted SharePoint Search) Allow-List Not Working

**Symptoms:** Copilot accesses sites not on the allow-list, or cannot access sites that are on the list.

**Diagnostic Steps:**

1. Verify RSS is enabled:
   ```powershell
   Get-SPOTenant | Select-Object RestrictedSearchEnabled
   ```

2. Get current allow-list:
   ```powershell
   Get-SPOSearchSiteConfiguration
   ```

3. Verify site URLs are exactly correct (no trailing slashes, correct case)

**Resolution:**
- Confirm RSS is enabled at tenant level
- Verify site URLs in allow-list are exact matches
- Note RSS has a maximum of 100 sites
- Allow 24 hours for changes to propagate

---

## Diagnostic Commands

```powershell
# Comprehensive IAG status check
$SiteUrl = "https://yourtenant.sharepoint.com/sites/TestSite"

Write-Host "=== IAG Diagnostic Report ===" -ForegroundColor Cyan

# Check site-specific settings
$Site = Get-SPOSite -Identity $SiteUrl
Write-Host "`nSite: $SiteUrl" -ForegroundColor Yellow
Write-Host "  RestrictContentOrgWideSearch: $($Site.RestrictContentOrgWideSearch)"
Write-Host "  RestrictedAccessControl: $($Site.RestrictedAccessControl)"
Write-Host "  RestrictedAccessControlGroups: $($Site.RestrictedAccessControlGroups)"
Write-Host "  SensitivityLabel: $($Site.SensitivityLabel)"

# Check tenant settings
$Tenant = Get-SPOTenant
Write-Host "`nTenant Settings:" -ForegroundColor Yellow
Write-Host "  RestrictedSearchEnabled: $($Tenant.RestrictedSearchEnabled)"

# Check for any RSS sites
Write-Host "`nRestricted SharePoint Search Sites:" -ForegroundColor Yellow
Get-SPOSearchSiteConfiguration | ForEach-Object {
    Write-Host "  - $($_.SiteUrl)"
}
```

---

## Escalation Path

1. **Level 1:** SharePoint Admin - Basic configuration issues
2. **Level 2:** Microsoft 365 Admin - License and tenant-level settings
3. **Level 3:** Microsoft Support - Product bugs or feature limitations
4. **Level 4:** AI Governance Committee - Policy exceptions

---

## How to Confirm Configuration is Active

### Via Portal

1. Navigate to **SharePoint Admin Center** > **Sites** > **Active sites**
2. Select the site
3. Open **Settings** tab
4. Verify "Restrict content from Microsoft 365 Copilot" shows **On**

### Via PowerShell

```powershell
# Quick status check
$SiteUrl = "https://yourtenant.sharepoint.com/sites/RegulatedSite"
$Site = Get-SPOSite -Identity $SiteUrl

if ($Site.RestrictContentOrgWideSearch -eq $true) {
    Write-Host "PASS: Site is restricted from Copilot" -ForegroundColor Green
}
else {
    Write-Host "FAIL: Site is NOT restricted from Copilot" -ForegroundColor Red
}
```

### Via Copilot Testing

1. As a user with site access, open Microsoft 365 Copilot
2. Ask a specific question about content from the restricted site
3. Verify Copilot does NOT return that content
4. Ask about content from an unrestricted site to confirm Copilot is working

---

[Back to Control 4.1](../../../controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
