# Verification & Testing: Control 1.25 - MIME Type Restrictions for File Uploads

**Last Updated:** February 2026

## Manual Verification Steps

### Test 1: Verify Blocked Extensions List Matches Zone Template

1. Navigate to Power Platform Admin Center → Environments → [Environment] → Settings → Privacy + Security
2. Locate the **Set blocked file extensions for attachments** field
3. Compare the configured extensions against the zone template
4. **EXPECTED:** Blocked extensions include all zone-appropriate extensions (44 for Zone 1, 45 for Zone 2, 55 for Zone 3). Use `Test-FsiMimeCompliance` for automated verification against the complete zone template.

### Test 2: Verify Blocked MIME Types Configured (Zone 2+)

1. Navigate to Power Platform Admin Center → Environments → [Zone 2/3 Environment] → Settings → Privacy + Security
2. Locate the **Set blocked mime types for attachments** field
3. Verify MIME types are populated
4. **EXPECTED:** Blocked MIME types include application/x-msdownload, application/x-msdos-program, application/x-bat, application/x-cmd, application/x-vbs, application/javascript, application/x-powershell, application/x-msi

### Test 3: Verify MIME Type Allowlist (Zone 2+)

1. Navigate to Power Platform Admin Center → Environments → [Zone 2/3 Environment] → Settings → Privacy + Security
2. Locate the **Set allowed mime types for attachments** field
3. Verify only approved MIME types are listed
4. **EXPECTED:** Allowed MIME types are limited to approved document and image types (application/pdf, image/png, image/jpeg, image/gif, text/plain, text/csv, and Office Open XML types)

### Test 4: Attempt Upload of Blocked File Type

1. Open a model-driven app connected to the target environment
2. Navigate to a record with a file attachment field
3. Attempt to upload a file with a blocked extension (e.g., .exe or .bat)
4. **EXPECTED:** Upload is rejected with an error message indicating the file type is not allowed

### Test 5: Verify DLP Policy Generating Alerts (Zone 2+)

1. Navigate to Microsoft Purview Compliance Portal → Data Loss Prevention → Activity explorer
2. Filter for Power Platform file upload events
3. Verify DLP policy matches are logged for blocked file type attempts
4. **EXPECTED:** DLP alerts are generated when users attempt to upload restricted file types in Zone 2 and Zone 3 environments

### Test 6: Verify Sentinel Queries Returning Data (Zone 3)

1. Navigate to Microsoft Sentinel → Logs
2. Run the KQL query from the Evidence Collection section below
3. Verify blocked upload events appear in the results
4. **EXPECTED:** Sentinel query returns records for blocked file upload attempts with environment name, user, file type, and timestamp

---

## Test Cases

| Test ID | Scenario | Expected Result | Pass/Fail |
|---------|----------|-----------------|-----------|
| TC-1.25-01 | Blocked extensions configured | All executable extensions listed in blocklist | |
| TC-1.25-02 | Blocked MIME types configured (Zone 2+) | Required MIME types present in blocklist | |
| TC-1.25-03 | Allowed MIME types allowlist (Zone 2+) | Only approved document and image types listed | |
| TC-1.25-04 | Blocked file upload rejected | Upload of .exe file returns error | |
| TC-1.25-05 | DLP alert on blocked upload (Zone 2+) | DLP policy match logged in Activity explorer | |
| TC-1.25-06 | Sentinel data for blocked uploads (Zone 3) | KQL query returns blocked upload events | |
| TC-1.25-07 | Allowed file upload accepted | Upload of approved file type (.pdf) succeeds | |
| TC-1.25-08 | Zone template compliance | Test-FsiMimeCompliance returns IsCompliant = True | |

---

## Evidence Collection Checklist

- [ ] Screenshot: PPAC blocked file extensions configuration
- [ ] Screenshot: PPAC blocked MIME types configuration (Zone 2+)
- [ ] Screenshot: PPAC allowed MIME types configuration (Zone 2+)
- [ ] Screenshot: Blocked file upload rejection error message
- [ ] Screenshot: DLP Activity explorer showing blocked upload event (Zone 2+)
- [ ] Export: Test-FsiMimeCompliance output per environment
- [ ] Export: Sentinel query results for blocked uploads (Zone 3)
- [ ] Export: Environment MIME configuration report (Get-FsiMimeConfig output)

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
