# Verification & Testing: Control 1.25 - MIME Type Restrictions for File Uploads

**Last Updated:** April 2026

## Manual Verification Steps

### Test 1: Verify Blocked Extensions List Matches Zone Template

1. Navigate to Power Platform Admin Center → Environments → [Environment] → Settings → **Product** → Privacy + Security
2. Locate the **Set blocked file extensions for attachments** field
3. Compare the configured extensions against the zone template **and** the Microsoft default list
4. **EXPECTED:** Blocked extensions include all zone-appropriate extensions (44 for Zone 1, 45 for Zone 2, 55 for Zone 3) **and the Microsoft defaults are not removed**. Use `Test-FsiMimeCompliance` for automated verification against the complete zone template.

### Test 2: Verify Blocked MIME Types Configured (Zone 2+)

1. Navigate to Power Platform Admin Center → Environments → [Zone 2/3 Environment] → Settings → **Product** → Privacy + Security
2. Locate the **Set blocked mime types for attachments** field
3. Verify MIME types are populated
4. **EXPECTED:** Blocked MIME types include `application/x-msdownload`, `application/x-msdos-program`, `application/x-bat`, `application/x-cmd`, `application/x-vbs`, `application/javascript`, `application/x-powershell`, `application/x-msi`

### Test 3: Verify MIME Type Allowlist (Zone 2+)

1. Navigate to Power Platform Admin Center → Environments → [Zone 2/3 Environment] → Settings → **Product** → Privacy + Security
2. Locate the **Set allowed mime types for attachments** field
3. Verify only approved MIME types are listed
4. **EXPECTED:** Allowed MIME types are limited to approved document and image types (`application/pdf`, `image/png`, `image/jpeg`, `image/gif`, `text/plain`, `text/csv`, and Office Open XML types). Confirm the agent owner has documented business justification for each entry.

### Test 4: Attempt Upload of Blocked File Type (PPAC Boundary Test)

1. Open a model-driven app connected to the target environment
2. Navigate to a record with a file attachment field
3. Attempt to upload a file with a blocked extension (e.g., `.exe` or `.bat`)
4. **EXPECTED:** Upload is rejected with an error message indicating the file type is not allowed

### Test 5: Per-Agent File Upload Toggle Attestation (Copilot Studio)

1. Open [Copilot Studio](https://copilotstudio.microsoft.com) → select agent → **Settings** → **Security**
2. Confirm the **File Upload** toggle state matches the documented governance decision for the agent
3. If File Upload is **On**, confirm the **Allowed file types** list is the minimum set required by the agent's documented purpose
4. **EXPECTED:** Toggle state and allowed-type list are documented per agent with screenshot evidence stored under `maintainers-local/tenant-evidence/1.25/`. No production Zone 2/3 agent has File Upload enabled without a documented business justification.

### Test 6: Spoofed-MIME Magic-Byte Test (Zone 3, Defender for Cloud Apps)

1. Create a test file by renaming a small Windows executable (e.g., `notepad.exe`) to `test.pdf`
2. Upload the renamed file via a test channel into a SharePoint library scanned by Defender for Cloud Apps
3. Wait up to 15 minutes for Defender for Cloud Apps API connector scan
4. Navigate to **Defender XDR → Cloud apps → Files** and filter by **MIME type (true type) = application/x-msdownload**
5. **EXPECTED:** The file is flagged, quarantine action executed, and an alert is generated. Sentinel receives the alert via SIEM connector. PPAC alone would not catch this case because the file extension `.pdf` is allowlisted.

### Test 7: Verify Copilot Studio Knowledge-Source File-Type Restrictions

1. Open the agent in Microsoft Copilot Studio → **Knowledge** tab
2. Attempt to add a file knowledge source with an unsupported format (e.g., `.exe`, `.zip`, `.mp4`)
3. **EXPECTED:** Copilot Studio rejects the upload with an unsupported-format message. Supported knowledge formats per Microsoft Learn (April 2026): `.pdf`, `.docx`, `.xlsx`, `.pptx`, `.txt`, `.md`, `.csv`, `.html`, `.json`, `.yaml`, and selected others (executable/audio/video formats are not supported).

### Test 8: Verify DLP Policy Generating Alerts (Zone 2+)

1. Navigate to Microsoft Purview portal → **Data Loss Prevention** → **Activity explorer**
2. Filter for Power Platform file upload events
3. Verify DLP policy matches are logged for blocked file type attempts
4. **EXPECTED:** DLP alerts are generated when users attempt to upload restricted file types in Zone 2 and Zone 3 environments

### Test 9: Verify Sentinel Queries Returning Data (Zone 3)

1. Navigate to Microsoft Sentinel → **Logs**
2. Run the KQL query from the Evidence Collection section below
3. Verify blocked upload events appear in the results
4. **EXPECTED:** Sentinel query returns records for blocked file upload attempts with environment name, user, file type, and timestamp

---

## Test Cases

| Test ID | Scenario | Expected Result | Pass/Fail |
|---------|----------|-----------------|-----------|
| TC-1.25-01 | Blocked extensions configured (Microsoft defaults retained + organizational additions) | Defaults present; zone-template extensions present | |
| TC-1.25-02 | Blocked MIME types configured (Zone 2+) | Required MIME types present in blocklist | |
| TC-1.25-03 | Allowed MIME types allowlist (Zone 2+) | Only approved document and image types listed; each entry has documented justification | |
| TC-1.25-04 | Blocked file upload rejected at PPAC boundary | Upload of `.exe` file returns error | |
| TC-1.25-05 | Per-agent File Upload toggle documented | Screenshot evidence captured per production agent | |
| TC-1.25-06 | Per-agent allowed file types follow least-privilege | Allowed list ⊆ environment allowlist; each entry justified | |
| TC-1.25-07 | DLP alert on blocked upload (Zone 2+) | DLP policy match logged in Activity explorer | |
| TC-1.25-08 | Defender for Cloud Apps magic-byte detection (Zone 3) | Renamed `.exe`-as-`.pdf` quarantined and alerted | |
| TC-1.25-09 | Copilot Studio knowledge-source rejection of unsupported format | Upload of `.exe`/`.zip`/`.mp4` rejected by Copilot Studio | |
| TC-1.25-10 | Sentinel data for blocked uploads (Zone 3) | KQL query returns blocked upload events | |
| TC-1.25-11 | Allowed file upload accepted | Upload of approved file type (`.pdf`) succeeds | |
| TC-1.25-12 | Zone template compliance (automated) | `Test-FsiMimeCompliance` returns `IsCompliant = True` | |

---

## Evidence Collection Checklist

- [ ] Screenshot: PPAC blocked file extensions configuration (per environment)
- [ ] Screenshot: PPAC blocked MIME types configuration (Zone 2+)
- [ ] Screenshot: PPAC allowed MIME types configuration (Zone 2+)
- [ ] Screenshot: Blocked file upload rejection error message
- [ ] Screenshot: Copilot Studio per-agent **File Upload** toggle state (per production agent, Zone 2/3)
- [ ] Screenshot: Copilot Studio per-agent **Allowed file types** list with documented business justification
- [ ] Screenshot: Defender for Cloud Apps file policy showing **Enabled** state and quarantine action (Zone 3)
- [ ] Screenshot: DLP Activity explorer showing blocked upload event (Zone 2+)
- [ ] Export: `Test-FsiMimeCompliance` JSON output per environment with SHA-256 evidence hash
- [ ] Export: Sentinel query results for blocked uploads (Zone 3)
- [ ] Export: Environment MIME configuration report (`Get-FsiMimeConfig` JSON output)
- [ ] Storage: All evidence stored under `maintainers-local/tenant-evidence/1.25/` (gitignored)

---

## Attestation Statement Template

```markdown
## Control 1.25 Attestation - MIME Type Restrictions for File Uploads

**Organization:** [Organization Name]
**Control Owner:** [Name/Role]
**Date:** [Date]

I attest that:

1. Blocked file extensions are configured for all Power Platform environments:
   - Zone 1 environments: [Count] — executable extensions blocked
   - Zone 2 environments: [Count] — executable extensions and MIME types blocked
   - Zone 3 environments: [Count] — executable extensions, MIME types blocked, and allowlist configured
2. MIME type restrictions are applied per governance zone requirements:
   - Blocked MIME types configured for Zone 2 and Zone 3: [Yes/No]
   - Allowed MIME types allowlist configured for Zone 3: [Yes/No]
3. File upload restrictions were tested and validated:
   - Blocked file types are rejected on upload: [Yes/No]
   - DLP policies are generating alerts for Zone 2+: [Yes/No]
4. Compliance validation was run using Test-FsiMimeCompliance:
   - Environments compliant: [Count] of [Total]
   - Environments with findings: [Count]
5. Exceptions documented and approved per governance process: [Count]

**Total Environments Assessed:** [Count]
**Compliant Environments:** [Count]
**Non-Compliant Environments:** [Count]

**Signature:** _______________________
**Date:** _______________________
```

---

## Zone-Specific Testing Requirements

| Zone | Test Frequency | Blocked Extensions Review | MIME Types Review | Upload Testing | DLP Validation | Sentinel Monitoring |
|------|----------------|---------------------------|-------------------|----------------|----------------|---------------------|
| Zone 1 | Quarterly | Quarterly | N/A | Quarterly | N/A | N/A |
| Zone 2 | Monthly | Monthly | Monthly | Monthly | Monthly | Optional |
| Zone 3 | Weekly | Weekly | Weekly | Weekly | Weekly | Weekly |

---

## KQL Queries for Evidence

> **Important:** The operation names and `AdditionalProperties` field names used in the queries below are illustrative examples. Actual values vary by tenant configuration and connector version. Before using these queries in production, run `PowerPlatformAdminActivity | take 10` in your Sentinel workspace to inspect available fields, and run `PowerPlatformAdminActivity | distinct Operation | sort by Operation` to identify the correct operation names for your environment.

### Query Blocked File Upload Events (Sentinel)

```kql
PowerPlatformAdminActivity
| where TimeGenerated > ago(30d)
| where Operation == "FileUploadBlocked" or Operation contains "MimeTypeRestriction"
| project
    TimeGenerated,
    EnvironmentName = tostring(AdditionalProperties.EnvironmentName),
    UserPrincipalName = UserId,
    BlockedFileType = tostring(AdditionalProperties.FileExtension),
    BlockedMimeType = tostring(AdditionalProperties.MimeType),
    Operation
| order by TimeGenerated desc
```

### Query Exception Usage (Sentinel)

```kql
PowerPlatformAdminActivity
| where TimeGenerated > ago(30d)
| where Operation contains "MimeTypeException" or Operation contains "FileExtensionException"
| project
    TimeGenerated,
    EnvironmentName = tostring(AdditionalProperties.EnvironmentName),
    UserPrincipalName = UserId,
    ExceptionType = tostring(AdditionalProperties.ExceptionType),
    ApprovedBy = tostring(AdditionalProperties.ApprovedBy),
    Justification = tostring(AdditionalProperties.Justification)
| order by TimeGenerated desc
```

### Query MIME Configuration Changes (Sentinel)

```kql
PowerPlatformAdminActivity
| where TimeGenerated > ago(90d)
| where Operation contains "UpdateEnvironmentSettings"
| where AdditionalProperties has "blockedmime" or AdditionalProperties has "blockedextension" or AdditionalProperties has "allowedmime"
| project
    TimeGenerated,
    EnvironmentName = tostring(AdditionalProperties.EnvironmentName),
    ModifiedBy = UserId,
    SettingChanged = tostring(AdditionalProperties.SettingName),
    OldValue = tostring(AdditionalProperties.OldValue),
    NewValue = tostring(AdditionalProperties.NewValue)
| order by TimeGenerated desc
```

---

[Back to Control 1.25](../../../controls/pillar-1-security/1.25-mime-type-restrictions.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
