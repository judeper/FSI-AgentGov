# Control 4.8: Troubleshooting — Item-Level Permission Scanning for Agent Knowledge Sources

> **Parent Control:** [Control 4.8 — Item-Level Permission Scanning](../../../controls/pillar-4-sharepoint/4.8-item-level-permission-scanning-agent-knowledge-sources.md)
>
> **Related Playbooks:** [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md)

---

## Overview

This playbook covers common issues encountered during item-level permission scanning of agent knowledge source libraries, with diagnosis steps and resolutions.

---

## Common Issues

### Issue 1: Scanner Fails with Permission Error

**Symptoms:**

- Script terminates with "Access Denied" or "403 Forbidden" error
- Error message: "The current user does not have sufficient permissions to perform this operation"
- Scan starts but skips certain sites or libraries

**Diagnosis:**

```powershell
# Check current user permissions on the target site
Connect-PnPOnline -Url "https://<tenant>.sharepoint.com/sites/<sitename>" -Interactive
Get-PnPSiteCollectionAdmin

# Verify SharePoint Admin role assignment
Connect-MgGraph -Scopes "RoleManagement.Read.Directory"
$SharePointAdminRole = Get-MgDirectoryRole | Where-Object { $_.DisplayName -eq "SharePoint Administrator" }
Get-MgDirectoryRoleMember -DirectoryRoleId $SharePointAdminRole.Id
```

**Resolution:**

1. Ensure the scanning account has **SharePoint Administrator** role OR **Site Collection Administrator** on each target site
2. For Graph API-based scanning, verify the app registration has `Sites.FullControl.All` permission
3. If using a service account, confirm it is not blocked by Conditional Access policies
4. For sites with Restricted Access Control (RAC), the scanning account must be in the RAC security group

!!! warning "RAC-Protected Sites"
    Sites configured with Restricted Access Control (Control 4.1) limit access to members of a specified security group. The scanning service account must be added to this group, or scanning will fail with an access denied error.

---

### Issue 2: Scan Times Out on Large Libraries

**Symptoms:**

- Script runs for extended periods (>2 hours) without completing
- PowerShell session disconnects or times out
- Partial CSV output with incomplete results

**Diagnosis:**

```powershell
# Check library item count
Connect-PnPOnline -Url "https://<tenant>.sharepoint.com/sites/<sitename>" -Interactive
$Library = Get-PnPList -Identity "Documents"
Write-Host "Total items: $($Library.ItemCount)"
Write-Host "Large library threshold: 5,000 items"
```

**Resolution:**

1. **Increase PageSize** — Adjust the `-PageSize` parameter:
   ```powershell
   Get-PnPListItem -List "Documents" -PageSize 2000
   ```
2. **Scan in batches** — Divide the library by folder path and scan each folder separately
3. **Use batch mode** — Configure `item-scope-config.json` with `maxItemsPerLibrary` limit and run multiple passes
4. **Azure Automation** — For libraries over 10,000 items, use Azure Automation with extended timeout (Zone 3 recommended approach)
5. **Filter by date** — Scan only items modified since the last scan:
   ```powershell
   $CutoffDate = (Get-Date).AddDays(-30).ToString("yyyy-MM-ddTHH:mm:ssZ")
   Get-PnPListItem -List "Documents" -Query "<View><Query><Where><Geq><FieldRef Name='Modified'/><Value Type='DateTime' IncludeTimeValue='TRUE'>$CutoffDate</Value></Geq></Where></Query></View>"
   ```

---

### Issue 3: Sensitivity Labels Not Detected

**Symptoms:**

- Scan output shows "None" for SensitivityLabel on items known to have labels
- Risk classification defaults to LOW for items that should be CRITICAL or HIGH
- Label detection works in SharePoint UI but not via PowerShell

**Diagnosis:**

```powershell
# Check if sensitivity label column is available
Connect-PnPOnline -Url "https://<tenant>.sharepoint.com/sites/<sitename>" -Interactive
$Item = Get-PnPListItem -List "Documents" -Id 1
$Item.FieldValues.Keys | Where-Object { $_ -match "Compliance|Label|Sensitivity" }

# Check specific label fields
Write-Host "ComplianceTag: $($Item.FieldValues['_ComplianceTag'])"
Write-Host "IpLabelId: $($Item.FieldValues['_IpLabelId'])"
```

**Resolution:**

1. **Field name mismatch** — Verify the correct field name for sensitivity labels in your tenant:
   - `_ComplianceTag` — retention/sensitivity label display name
   - `_IpLabelId` — sensitivity label GUID
   - Check both fields and use whichever is populated
2. **Label not synced** — Per Microsoft Learn, sensitivity labels can take **up to 24 hours** to sync to SharePoint item metadata. Re-scan after the sync window before treating findings as authoritative.
3. **Permissions** — The scanning account may need `InformationProtectionPolicy.Read` permission in Microsoft Graph to read label metadata
4. **Update config** — Ensure `item-scope-config.json` label names match your organization's label taxonomy exactly (case-sensitive)

---

### Issue 4: Configuration File Errors

**Symptoms:**

- Script fails with "Cannot parse configuration file" or JSON parse error
- Risk classification does not match expected behavior
- Labels present in config are not matched during scanning

**Diagnosis:**

```powershell
# Validate JSON syntax
try {
    $Config = Get-Content -Path "./config/item-scope-config.json" -Raw | ConvertFrom-Json
    Write-Host "Configuration file is valid JSON." -ForegroundColor Green
    Write-Host "Critical labels defined: $($Config.sensitivityLabels.critical.Count)"
    Write-Host "High labels defined: $($Config.sensitivityLabels.high.Count)"
}
catch {
    Write-Host "Configuration file has JSON errors: $_" -ForegroundColor Red
}
```

**Resolution:**

1. **Validate JSON** — Use the diagnostic command above to check for syntax errors
2. **Label name matching** — Confirm label names match exactly (including spaces and capitalization)
3. **Missing sections** — Ensure all required sections exist: `sensitivityLabels`, `riskThresholds`, `scanSettings`
4. **Encoding** — Save the config file as UTF-8 without BOM

---

### Issue 5: Stale Scan Results After Remediation

**Symptoms:**

- Items remediated (permissions changed) still show as CRITICAL/HIGH in scan output
- Pre-deployment gate remains BLOCKED despite completed remediation
- Dashboard shows outdated risk data

**Diagnosis:**

```powershell
# Check scan file timestamps
$ScanFiles = Get-ChildItem -Path "./output" -Filter "item-permissions-scan-*.csv" | Sort-Object LastWriteTime -Descending
$ScanFiles | Select-Object Name, LastWriteTime | Format-Table

# Compare latest scan date with remediation date
$LatestScan = $ScanFiles | Select-Object -First 1
Write-Host "Latest scan: $($LatestScan.LastWriteTime)"
Write-Host "Is this after remediation? Verify and re-scan if needed."
```

**Resolution:**

1. **Re-run scan** — Always re-scan after remediation to verify changes took effect:
   ```powershell
   .\Get-KnowledgeSourceItemPermissions.ps1 -AdminUrl "https://<tenant>-admin.sharepoint.com" -ConfigPath "./config/item-scope-config.json" -OutputPath "./output"
   ```
2. **Permission propagation delay** — SharePoint permission changes may take up to 15 minutes to propagate. Wait and re-scan.
3. **Cache invalidation** — Clear the PnP PowerShell connection cache:
   ```powershell
   Disconnect-PnPOnline
   Connect-PnPOnline -Url $SiteUrl -Interactive -ForceAuthentication
   ```
4. **Archive old results** — Move previous scan outputs to an archive folder to avoid confusion

---

### Issue 6: Library Exceeds Copilot Studio Knowledge Source Limits

**Symptoms:**

- Library has more than 1,000 files, more than 50 folders, or more than 10 layers of subfolders
- Agent appears to ignore some content even though items exist in the library
- Scan reports items that the agent never returns

**Diagnosis:**

```powershell
# Check library size against Copilot Studio SharePoint limits (per Microsoft Learn)
Connect-PnPOnline -Url "https://<tenant>.sharepoint.com/sites/<sitename>" -Interactive
$Library = Get-PnPList -Identity "Documents"
$Items = Get-PnPListItem -List $Library -PageSize 500
$FileCount = ($Items | Where-Object { $_.FileSystemObjectType -eq "File" }).Count
$FolderCount = ($Items | Where-Object { $_.FileSystemObjectType -eq "Folder" }).Count
Write-Host "Files: $FileCount (limit: 1000)"
Write-Host "Folders: $FolderCount (limit: 50)"
```

**Resolution:**

1. **Reduce library scope** — Move out-of-scope content out of the agent-connected library, or change the knowledge source path to a narrower folder
2. **Split into multiple libraries** — Each library remains its own knowledge source with its own limits
3. **Continue scanning the full library** — Item-level scanning still applies to unindexed content because permissions remain a sharing risk if the library is later restructured or limits change
4. **Document the gap** — Note which items are not currently indexed by the agent so that examiner inquiries can be answered accurately

!!! info "Why scan items the agent will not retrieve"
    Items that exceed Microsoft Copilot Studio's indexing limits are not currently served by the agent, but they remain a SharePoint oversharing risk. They may become indexed if Microsoft adjusts limits, the library is restructured, or files are moved into the indexed scope. Continuing to scan supports the full SharePoint posture rather than only the current agent retrieval surface.

---

## Diagnostic Commands

### Verify PnP PowerShell Connection

```powershell
# Test PnP connection and permissions
Connect-PnPOnline -Url "https://<tenant>.sharepoint.com/sites/<sitename>" -Interactive
$Web = Get-PnPWeb
Write-Host "Connected to: $($Web.Title) ($($Web.Url))" -ForegroundColor Green
$CurrentUser = Get-PnPProperty -ClientObject $Web -Property CurrentUser
Write-Host "Authenticated as: $($CurrentUser.Title) ($($CurrentUser.Email))" -ForegroundColor Cyan
```

### Check Library Permissions Structure

```powershell
# Audit unique permissions count in a library
$Library = Get-PnPList -Identity "Documents"
$Items = Get-PnPListItem -List "Documents" -PageSize 500
$UniqueCount = 0
foreach ($Item in $Items) {
    $HasUnique = Get-PnPProperty -ClientObject $Item -Property "HasUniqueRoleAssignments"
    if ($HasUnique) { $UniqueCount++ }
}
Write-Host "Library: $($Library.Title)"
Write-Host "Total items: $($Library.ItemCount)"
Write-Host "Items with unique permissions: $UniqueCount"
Write-Host "Percentage with unique perms: $([math]::Round(($UniqueCount / $Library.ItemCount) * 100, 1))%"
```

### Verify Scan Output Integrity

```powershell
# Validate scan output CSV structure
$LatestScan = Get-ChildItem -Path "./output" -Filter "item-permissions-scan-*.csv" |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1

if ($LatestScan) {
    $Results = Import-Csv -Path $LatestScan.FullName
    $RequiredColumns = @("SiteUrl", "LibraryName", "ItemId", "FileName", "FilePath",
                         "SensitivityLabel", "SharingScopes", "RiskLevel", "HasUniquePerms", "ScannedDate")

    $MissingColumns = $RequiredColumns | Where-Object { $_ -notin $Results[0].PSObject.Properties.Name }

    if ($MissingColumns) {
        Write-Host "Missing columns: $($MissingColumns -join ', ')" -ForegroundColor Red
    } else {
        Write-Host "All required columns present." -ForegroundColor Green
    }

    Write-Host "Total rows: $($Results.Count)"
    Write-Host "Risk distribution:"
    $Results | Group-Object RiskLevel | ForEach-Object {
        Write-Host "  $($_.Name): $($_.Count)"
    }
} else {
    Write-Host "No scan output files found." -ForegroundColor Red
}
```

---

## Escalation Path

| Severity | Condition | Escalation Path | SLA |
|----------|-----------|-----------------|-----|
| **P1 — Critical** | CRITICAL items detected in production agent knowledge sources | AI Governance Lead → CISO → Immediate remediation or agent disconnection | 4 hours |
| **P2 — High** | Scanner unable to access agent knowledge source libraries | SharePoint Admin → IT Operations → Resolve access issues | 24 hours |
| **P3 — Medium** | Scan schedule missed or incomplete results | SharePoint Admin → AI Governance Lead → Investigate and reschedule | 5 business days |
| **P4 — Low** | Configuration updates needed (label taxonomy changes) | SharePoint Admin → Update config → Run validation | Next scheduled maintenance |

---

## Prevention Best Practices

1. **Test scanning in non-production first** — Validate scripts and configuration against a test site before scanning production knowledge sources
2. **Monitor SharePoint sharing alerts** — Configure SharePoint Admin alerts for new sharing activity on agent-connected libraries to trigger on-demand scans
3. **Review config on label changes** — When organizational sensitivity labels are updated in Microsoft Purview, update `item-scope-config.json` immediately
4. **Validate permissions before connecting** — Establish a workflow where knowledge source library permissions are reviewed before connecting to a new agent
5. **Use RAC where possible** — Apply Restricted Access Control (Control 4.1) on agent knowledge source sites to limit access at the site level, reducing item-level oversharing risk
6. **Document exceptions** — Any risk acceptance (e.g., deferred MEDIUM remediation) must be documented with business justification, approver, and expiration date
7. **Keep scanning tools updated** — Regularly update `Get-KnowledgeSourceItemPermissions.ps1` from the FSI-AgentGov-Solutions repository to incorporate fixes and improvements

---

## Related Resources

- [Microsoft Learn: Copilot Studio SharePoint knowledge source](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-sharepoint)
- [Microsoft Learn: Copilot Studio requirements and quotas (SharePoint limits)](https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-quotas)
- [Microsoft Learn: SharePoint item-level permissions](https://learn.microsoft.com/en-us/sharepoint/modern-experience-sharing-permissions)
- [Microsoft Learn: PnP PowerShell](https://pnp.github.io/powershell/)
- [Microsoft Learn: Sensitivity labels in SharePoint](https://learn.microsoft.com/en-us/purview/sensitivity-labels-sharepoint-onedrive-files)
- [FSI-AgentGov-Solutions: agent-knowledge-source-scanner](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-knowledge-source-scanner)
- [Control 4.8 — Verification & Testing](verification-testing.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
