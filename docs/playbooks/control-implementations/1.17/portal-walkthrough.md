# Portal Walkthrough: Control 1.17 - Endpoint Data Loss Prevention (Endpoint DLP)

**Last Updated:** January 2026
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

1. Open [Microsoft Purview](https://compliance.microsoft.com)
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

---

## Configuration by Governance Level

| Setting | Baseline (Tier 1) | Recommended (Tier 2) | Regulated (Tier 3) |
|---------|-------------------|----------------------|-------------------|
| **USB Transfer** | Audit | Block with override | Block |
| **Cloud Upload** | Audit | Block with override | Block |
| **Print** | Allowed | Audit | Block |
| **Clipboard** | Allowed | Audit to unallowed | Block |
| **Bluetooth** | Allowed | Block | Block |
| **Network Share** | Audit | Audit | Block to unauthorized |

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
