# Troubleshooting: Control 1.25 - MIME Type Restrictions for File Uploads

**Last Updated:** May 2026

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| Blocked file type still uploadable | Extension not in blocklist or typo in configuration | Verify extension spelling and semicolon separators; confirm Microsoft defaults are not removed |
| MIME type not recognized by platform | Incorrect MIME type string or unsupported format | Use standardized IANA MIME type identifiers |
| Allowlist silently overrides blocklist | When `allowedmimetypes` is set, only that list is honored | Confirm allowlist is complete; do not rely on blocklist as a fallback once allowlist is active |
| Zone template application fails | Insufficient permissions or environment locked | Verify Power Platform Admin role; check environment state |
| DLP policy not triggering on file uploads | DLP policy not scoped to Power Platform or connector | Review DLP policy scope in Microsoft Purview portal |
| Defender for Cloud Apps file policy not flagging spoofed MIME | API connector not enabled for the target SaaS app, or scan not yet completed | Verify connector status in Defender XDR → Cloud apps → Connected apps; allow up to 15 min for near-real-time scan |
| Sentinel query returns no results | Diagnostic settings not configured or data latency | Enable Power Platform admin activity connector in Sentinel |
| FsiMimeControl module import errors | Module not found or PowerShell version mismatch | Import module from repository path and verify PowerShell 7.0+ |
| Microsoft Copilot Studio per-agent toggle reverts after save | Stale browser session or maker without environment-level rights | Clear session, re-authenticate as AI Administrator or environment maker |
| Knowledge-source upload fails for supported format | File >512 MB, password-protected, or has sensitivity label | Check Copilot Studio quotas; remove password protection; review sensitivity label policy |
| SharePoint blocked-extension list ignored on browser upload | SharePoint tenant blocked-file-types only blocks the OneDrive sync client, not browser uploads | Use PPAC + Defender for Cloud Apps for browser-upload coverage |

---

## Detailed Troubleshooting

### Issue: Blocked File Type Still Uploadable

**Symptoms:** Users can successfully upload files with extensions that should be blocked (e.g., .exe, .bat)

**Resolution:**

1. Navigate to PPAC → Environments → [Environment] → Settings → Privacy + Security
2. Check the **Set blocked file extensions for attachments** field
3. Verify the target extension is listed (without the dot)
4. Check for typos or missing semicolon separators
5. Confirm the setting was saved (click **Save** if pending)
6. Clear browser cache and retry the upload test

**Portal Path:**
```
Power Platform Admin Center → Environments → [Environment] → Settings → Product → Privacy + Security
```

> **Note:** Changes may take up to 15 minutes to propagate across all sessions. If the issue persists after 15 minutes, verify the environment ID matches the target environment.

---

### Issue: MIME Type Not Recognized by Platform

**Symptoms:** Configured blocked MIME type does not prevent uploads of the target file type

**Resolution:**

1. Verify the MIME type string uses the correct IANA format (e.g., `application/x-msdownload` not `msdownload`)
2. Check that the MIME type is supported by Power Platform's validation engine
3. Test with a known-supported MIME type to isolate the issue
4. Consider using file extension blocking as a complementary control
5. Common corrections:
   - `application/exe` → `application/x-msdownload`
   - `application/bat` → `application/x-bat`
   - `text/javascript` → `application/javascript`

---

### Issue: Zone Template Application Fails

**Symptoms:** `Set-FsiMimeConfig` returns an error when applying a zone template

**Resolution:**

1. Verify your account has Power Platform Admin or Entra Global Admin role
2. Check the environment is not in a locked or read-only state:
   ```powershell
   $config = Get-FsiMimeConfig -DataverseUrl 'https://org.crm.dynamics.com' -AccessToken $token
   Write-Host "Organization ID: $($config.OrganizationId)"
   ```
3. Verify the Dataverse URL is correct (copy from PPAC → Environments → Details)
4. Check network connectivity to the Dataverse Web API
5. If the environment is managed by another admin, coordinate before applying changes

---

### Issue: DLP Policy Not Triggering on File Uploads

**Symptoms:** DLP alerts are not generated when users upload restricted file types

**Resolution:**

1. Navigate to Microsoft Purview portal → Data Loss Prevention → Policies
2. Verify a DLP policy exists that covers Power Platform connectors
3. Check the policy scope includes the target environment
4. Verify the policy is in **Enforce** mode (not **Test** or **Off**)
5. Allow up to 24 hours for new DLP policies to take effect
6. Check Activity explorer for recent events to rule out display delay

**Portal Path:**
```
Microsoft Purview portal → Data Loss Prevention → Policies → [Policy Name]
```

---

### Issue: Sentinel Query Returns No Results

**Symptoms:** KQL queries for blocked upload events return empty result sets

**Resolution:**

1. Verify the Power Platform admin activity data connector is enabled in Sentinel:
   - Navigate to Microsoft Sentinel → Data connectors
   - Search for **Power Platform** and verify status is **Connected**
2. Check that diagnostic settings include admin activity events
3. Verify the time range in the query matches the test period (default is 30 days)
4. Confirm at least one blocked upload attempt occurred in the query time range
5. Allow 15-30 minutes for event ingestion latency after a test upload

---

### Issue: FsiMimeControl Module Import Errors

**Symptoms:** `Import-Module FsiMimeControl` fails with module not found or version errors

**Resolution:**

1. Verify PowerShell version is 7.0 or later:
   ```powershell
   $PSVersionTable.PSVersion
   ```
2. Import the module from the repository path:
   ```powershell
   Import-Module ./scripts/governance/FsiMimeControl.psm1 -Force
   ```
3. Verify the module file exists at the expected path:
   ```powershell
   Test-Path ./scripts/governance/FsiMimeControl.psm1
   ```
4. Check for module conflicts:
   ```powershell
   Get-Module -Name FsiMimeControl -ListAvailable
   ```

---

## Escalation Path

1. **Power Platform Admin** — Environment settings, MIME configuration, permissions
2. **AI Administrator** — Per-agent File Upload toggle, allowed file types, knowledge-source ingestion
3. **Entra Security Admin** — Defender for Cloud Apps file policy tuning, magic-byte detection rules
4. **Purview Compliance Admin** — DLP policy scope, sensitive-info content inspection
5. **SOC Analyst** — Sentinel connector, KQL query authoring, alert triage
6. **Microsoft Support** — Platform-level issues with file restrictions or Dataverse API

---

## Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| Extension-based blocking only (no content inspection) | Renamed files may bypass extension checks | Use both extension and MIME type blocking together |
| MIME type validation depends on client-reported type | Spoofed MIME types may pass initial check | Layer with DLP policies for content-level inspection |
| Settings per environment (not per app) | All apps in an environment share the restriction | Use separate environments for different restriction levels |
| No built-in audit trail for setting changes | Requires Sentinel connector for change tracking | Enable Power Platform admin activity connector in Sentinel |
| Allowlist overrides blocklist | If allowlist is set, blocklist is not evaluated | Use allowlist approach for Zone 3; blocklist for Zone 1-2 |
| `allowedmimetypes` field may not be supported | Older Dataverse versions may not expose the allowed MIME types field | Set-FsiMimeConfig will warn and apply remaining settings; configure allowlist manually in PPAC portal or request environment upgrade |
| Propagation delay up to 15 minutes | Recent changes may not be enforced immediately | Wait 15 minutes before testing after configuration changes |

---

## Diagnostic Commands

### Check Current MIME Configuration

```powershell
Get-FsiMimeConfig -DataverseUrl 'https://org.crm.dynamics.com' -AccessToken $token | Format-List
```

### Verify Module Is Loaded

```powershell
Get-Module -Name FsiMimeControl | Format-Table Name, Path -AutoSize
```

### Quick Compliance Check

```powershell
Test-FsiMimeCompliance -DataverseUrl 'https://org.crm.dynamics.com' -AccessToken $token -Zone 2
```

### List All Power Platform Environments

```powershell
Get-AdminPowerAppEnvironment | Format-Table DisplayName, EnvironmentName, @{N='Type';E={$_.Internal.properties.environmentType}}
```

### Export Configuration for Audit

```powershell
# Export MIME configuration for a specific environment
Get-FsiMimeConfig -DataverseUrl 'https://org.crm.dynamics.com' -AccessToken $token -OutputFormat JSON -OutputPath '.\MimeConfigAudit.json'
```

---

## Related Documentation

- [Microsoft Learn: Manage privacy and security settings (Power Platform)](https://learn.microsoft.com/en-us/power-platform/admin/settings-privacy-security)
- [Microsoft Learn: System Settings General tab — Set blocked file extensions](https://learn.microsoft.com/en-us/power-platform/admin/system-settings-dialog-box-general-tab)
- [Microsoft Learn: Dataverse File and Image Columns](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/file-attributes)
- [Microsoft Learn: Power Platform DLP Policies](https://learn.microsoft.com/en-us/power-platform/admin/wp-data-loss-prevention)
- [Microsoft Learn: Defender for Cloud Apps File Policies](https://learn.microsoft.com/en-us/defender-cloud-apps/data-protection-policies)
- [Microsoft Learn: Copilot Studio — Allow file input from users](https://learn.microsoft.com/en-us/microsoft-copilot-studio/image-input-analysis)
- [Microsoft Learn: Copilot Studio — Quotas and limits](https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-quotas)
- [Microsoft Learn: SharePoint — Block syncing of specific file types](https://learn.microsoft.com/en-us/sharepoint/block-file-types)
- [Microsoft Learn: Microsoft Sentinel Data Connectors](https://learn.microsoft.com/en-us/azure/sentinel/data-connectors-reference)

---

[Back to Control 1.25](../../../controls/pillar-1-security/1.25-mime-type-restrictions.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
