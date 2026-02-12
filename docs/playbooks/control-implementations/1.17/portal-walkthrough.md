# Portal Walkthrough: Control 1.17 - Endpoint Data Loss Prevention (Endpoint DLP)

**Last Updated:** February 2026
**Portal:** Microsoft Purview, Microsoft Defender for Endpoint
**Estimated Time:** 4-6 hours for initial deployment

## Prerequisites

- [ ] Microsoft 365 E5 or equivalent license
- [ ] Microsoft Defender for Endpoint deployed
- [ ] Purview Compliance Admin role
- [ ] Devices onboarded to Defender for Endpoint

---

## Step-by-Step Configuration

### Step 1: Verify Device Onboarding

1. Open [Microsoft Defender Portal](https://security.microsoft.com)
2. Navigate to **Assets** > **Devices**
3. Verify target devices appear with "Active" status
4. For new devices, follow onboarding process via:
   - Microsoft Intune
   - Group Policy
   - Local script

### Step 2: Enable Endpoint DLP

1. Open [Microsoft Purview](https://purview.microsoft.com)
2. Navigate to **Data loss prevention** > **Endpoint DLP settings**
3. Enable **Endpoint DLP**
4. Configure global settings:
   - Browser restrictions (Chrome, Firefox, Edge)
   - Unallowed apps list
   - Cloud services restrictions

### Step 3: Configure Restricted Applications

1. In Endpoint DLP settings > **Restricted apps**
2. Add unauthorized applications:
   ```
   - Telegram.exe
   - Discord.exe
   - WhatsApp.exe
   - Dropbox.exe (consumer)
   - GoogleDrive.exe (consumer)
   ```
3. Configure action: Block or Audit

### Step 4: Configure USB/Removable Media Restrictions

1. Navigate to **Endpoint DLP settings** > **Device properties**
2. Configure allowed USB devices:
   - Add approved hardware IDs (corporate-encrypted drives)
   - Block all other removable storage
3. Set action per zone:
   - Zone 1: Audit
   - Zone 2: Block with override
   - Zone 3: Block (no override)

### Step 5: Create Endpoint DLP Policy

1. Navigate to **Data loss prevention** > **Policies**
2. Create new policy:
   - Name: `FSI-Endpoint-DLP-Zone3`
   - Location: Devices
   - Conditions: Sensitive info types (financial data)
3. Configure actions:
   - USB transfer: Block
   - Cloud upload: Block
   - Print: Audit
   - Clipboard: Block to unallowed apps
4. Configure user notifications and policy tips

### Step 6: Enable Just-in-Time Protection

1. In Endpoint DLP settings
2. Enable **Always audit file activities for devices**
3. Configure offline cache for policy enforcement

### Step 7: Enable Browser-Based DLP for Edge

1. Navigate to **Microsoft Purview Portal** (https://purview.microsoft.com)
2. Go to **Solutions** > **Data loss prevention** > **Policies**
3. Create or edit a DLP policy
4. In **Locations**, add **Microsoft Edge for Business** as a monitored location
5. Configure policy rules to detect sensitive information types in browser interactions with AI web apps
6. Set actions to **Block**, **Warn**, or **Audit** when sensitive data is detected in AI app text fields

!!! tip "No Device Onboarding Required"
    Browser-based DLP in Edge for Business operates independently of Defender for Endpoint device onboarding. This provides immediate DLP protection for AI web app usage without waiting for full MDE deployment.

### Step 8: Configure Network Data Security

1. Navigate to **Microsoft Entra Admin Center** (https://entra.microsoft.com)
2. Go to **Global Secure Access** > **Security profiles**
3. Create or edit a security profile
4. Add DLP policy references to enforce sensitive data detection on network traffic
5. Configure traffic filtering rules to monitor connections to known AI service endpoints

---

## Configuration by Governance Level

| Setting | Baseline (Zone 1) | Recommended (Zone 2) | Regulated (Zone 3) |
|---------|-------------------|----------------------|-------------------|
| **USB Transfer** | Audit | Block with override | Block |
| **Cloud Upload** | Audit | Block with override | Block |
| **Print** | Allowed | Audit | Block |
| **Clipboard** | Allowed | Audit to unallowed | Block |
| **Bluetooth** | Allowed | Block | Block |
| **Network Share** | Audit | Audit | Block to unauthorized |
| **Browser DLP (Edge)** | Audit | Block with override | Block |
| **Network DLP (GSA)** | Not required | Recommended | Required |

---

## FSI Example Configuration

```yaml
Endpoint DLP Policy: FSI-Trading-Endpoints

Scope:
  Device Groups: Trading Floor Workstations
  Users: Trading Department

Protected Content:
  - SSN (U.S. Social Security Number)
  - Credit Card Number
  - Bank Account Number (U.S.)
  - Custom: FSI-CustomerAccountNumber

Restrictions:
  USB Storage:
    Action: Block
    Override: Not allowed
    Notification: "USB transfer of customer data is prohibited"

  Cloud Services:
    Action: Block
    Services: Personal Dropbox, Google Drive, iCloud
    Override: Not allowed

  Print:
    Action: Audit
    Log: All print operations with sensitive data

  Clipboard:
    Action: Block to restricted apps
    Restricted: Personal email, messaging apps

Notifications:
  User: Policy tip with explanation
  Admin: Alert on block events
```

---

## Validation

After completing these steps, verify:

- [ ] Devices appear in Purview with healthy status
- [ ] USB transfer of labeled content is blocked/audited
- [ ] Cloud upload to unauthorized services triggers action
- [ ] User receives policy tip notification
- [ ] Events appear in Activity Explorer

---

[Back to Control 1.17](../../../controls/pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
