# Portal Walkthrough: Control 1.25 - MIME Type Restrictions for File Uploads

**Last Updated:** February 2026
**Portal:** Power Platform Admin Center
**Estimated Time:** 20-30 minutes

## Prerequisites

- [ ] Power Platform Admin or Entra Global Admin role
- [ ] Access to Power Platform Admin Center
- [ ] Knowledge of organizational file type requirements per zone

---

## Step-by-Step Configuration

### Step 1: Navigate to Environment Settings

1. Open [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
2. Select **Environments** from the left navigation
3. Select the target environment (repeat for each environment per zone)
4. Click **Settings** in the top menu bar
5. Expand **Privacy + Security** (or **Features**, depending on environment type)

### Step 2: Configure Blocked File Extensions

1. Locate the **Set blocked file extensions for attachments** field
2. Enter a semicolon-separated list of file extensions to block
3. Recommended baseline extensions to block:

    ```
    exe;bat;cmd;com;vbs;js;wsf;scr;pif;msi;dll;ps1;reg;inf;hta;cpl;msp;mst
    ```

4. Click **Save** to apply changes

> **Note:** This setting applies to all file attachment fields in Dataverse tables within the selected environment.

### Step 3: Configure Blocked MIME Types (Zone 2+)

1. Locate the **Set blocked mime types for attachments** field
2. Enter a semicolon-separated list of MIME types to block
3. Recommended MIME types to block:

    ```
    application/x-msdownload;application/x-msdos-program;application/x-bat;application/x-cmd;application/x-vbs;application/javascript;application/x-powershell;application/x-msi
    ```

4. Click **Save** to apply changes

> **Note:** Blocking MIME types provides defense-in-depth beyond file extension restrictions, as it helps prevent renamed file bypass attempts.

### Step 4: Configure Allowed MIME Types (Zone 2+)

1. Locate the **Set allowed mime types for attachments** field
2. Enter a semicolon-separated allowlist of MIME types that are permitted
3. Recommended allowlist for regulated environments:

    ```
    application/pdf;image/png;image/jpeg;image/gif;text/plain;text/csv;application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;application/vnd.openxmlformats-officedocument.wordprocessingml.document;application/vnd.openxmlformats-officedocument.presentationml.presentation
    ```

4. Click **Save** to apply changes

> **Important:** When an allowlist is configured, only the listed MIME types are accepted. All other types are rejected regardless of the blocked list.

### Step 5: Review and Apply Zone Template

1. Review the configuration against the governance level table below
2. Verify the settings match the zone classification for the selected environment
3. Document the applied configuration in your governance records
4. Repeat Steps 1-4 for each environment within the zone

---

## Configuration by Governance Level

| Setting | Baseline (Zone 1) | Recommended (Zone 2) | Regulated (Zone 3) |
|---------|-------------------|----------------------|---------------------|
| **Blocked File Extensions** | Yes — executable types | Yes — executable types | Yes — executable types |
| **Blocked MIME Types** | Optional | Yes | Yes |
| **Allowed MIME Types (Allowlist)** | Not required | Recommended | Required |
| **DLP Policy for File Uploads** | Not required | Yes | Yes — with alerts |
| **Sentinel Monitoring** | Not required | Optional | Required |
| **Review Frequency** | Quarterly | Monthly | Weekly |
| **Exception Process** | Informal | Documented | Documented with approval |

---

## Validation

After completing these steps, verify:

- [ ] Blocked file extensions are configured for each environment
- [ ] Blocked MIME types are configured for Zone 2 and Zone 3 environments
- [ ] Allowed MIME types allowlist is configured for Zone 3 environments
- [ ] Configuration matches the governance level table for each environment zone
- [ ] Changes are documented in governance records

---

[Back to Control 1.25](../../../controls/pillar-1-security/1.25-mime-type-restrictions.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
