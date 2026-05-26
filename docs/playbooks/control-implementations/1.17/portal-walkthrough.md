# Portal Walkthrough: Control 1.17 — Endpoint Data Loss Prevention (Endpoint DLP)

**Last Updated:** May 2026
**Portals:** Microsoft Purview (`https://purview.microsoft.com`), Microsoft Defender (`https://security.microsoft.com`), Microsoft Intune (`https://intune.microsoft.com`), Microsoft Entra (`https://entra.microsoft.com`)
**Estimated Time:** 4–6 hours for an initial single-zone rollout; 1–2 days for full Zone 1/2/3 deployment with pilots

---

## Prerequisites

- [ ] Microsoft 365 E5 / E5 Compliance / E5 Security (or equivalent add-ons providing Endpoint DLP and Defender for Endpoint Plan 2)
- [ ] **Purview Compliance Admin** (canonical role) for DLP policy authoring
- [ ] **Entra Security Admin** (canonical role) for Defender for Endpoint device onboarding
- [ ] **Intune Administrator** for managed-device onboarding deployment
- [ ] **AI Administrator** awareness for coordination with Copilot governance (Control 1.5, 1.13)
- [ ] Sensitive Information Types (SITs) and labels in place — see Controls 1.5 and 1.13
- [ ] Pilot device groups identified (recommended: 5–10 devices per zone before broad rollout)
- [ ] Change Advisory Board (CAB) approval recorded for the policy mode transition (Test → Enforce)

!!! warning "Authoring shortcut, not enforcement shortcut"
    Endpoint DLP enforcement is **disruptive when misconfigured**. Always start in **Run policy in test mode with notifications** for at least one full business cycle (typically 7–14 days) before enabling enforcement. This approach helps meet FINRA Rule 3110(b) supervisory review obligations.

---

## Step 1 — Verify and Complete Device Onboarding

### Windows 10/11 (Intune-managed)

1. Sign in to **Microsoft Purview** (`https://purview.microsoft.com`).
2. In the left navigation, expand **Settings** → select **Device onboarding** → **Onboarding**.
3. From the **Deployment method** dropdown, select **Mobile Device Management / Microsoft Intune**.
4. Click **Download package** (this generates the `WindowsDefenderATPOnboardingPackage.zip` containing the Intune configuration profile).
5. Open **Microsoft Intune admin center** (`https://intune.microsoft.com`).
6. Navigate to **Endpoint security** → **Endpoint detection and response** → **Create policy**.
7. Select **Platform: Windows 10 and later** and **Profile: Endpoint detection and response**.
8. Upload the onboarding package and assign to the appropriate device group (e.g., `FSI-Zone3-Endpoints`).

### macOS

1. In **Purview > Settings > Device onboarding**, select **Mac onboarding**.
2. Follow the [Microsoft Learn macOS device onboarding guide](https://learn.microsoft.com/en-us/purview/device-onboarding-macos-overview) to install the Defender for Endpoint agent and grant Full Disk Access via Intune device configuration profiles.

### Verify Onboarding Status

1. In **Microsoft Purview > Settings > Device onboarding > Devices**, confirm target devices appear with **Onboarding status: Onboarded** and a recent **Last seen** timestamp.
2. Cross-check in **Microsoft Defender > Assets > Devices** for **Health state: Active** and **Sensor health: Healthy**.

!!! info "Allow 24 hours for first sync"
    Newly onboarded devices typically appear within 1–2 hours but may take up to 24 hours for full DLP telemetry to propagate.

---

## Step 2 — Configure Global Endpoint DLP Settings

1. In **Microsoft Purview**, navigate to **Solutions** → **Data Loss Prevention** → **Endpoint DLP settings**.
2. Configure each settings group below before authoring policies; these are tenant-wide and apply to all Endpoint DLP policies.

### File path exclusions

Add paths to exclude from monitoring (e.g., antivirus quarantine folders, line-of-business application working directories). Keep this list minimal in Zone 3.

### Restricted apps and app groups

1. Select **Restricted apps and app groups** → **Add or edit restricted apps**.
2. Create an app group named `FSI-Personal-Communication-Apps` and add executables:
   - `Telegram.exe`, `Discord.exe`, `WhatsApp.exe`, `Signal.exe`, `Slack.exe` (if unmanaged), `Zoom.exe` (if outside corporate tenant)
3. Create a second group `FSI-Consumer-Cloud-Sync` and add:
   - `Dropbox.exe`, `GoogleDriveFS.exe`, `iCloudDrive.exe`, `OneDrive.exe` (consumer profile path)
4. Set the default action: **Audit only** for Zone 1, **Block with override** for Zone 2, **Block** for Zone 3.

### Removable storage device groups

1. Select **Removable storage device groups** → **Add removable storage device group**.
2. Create `FSI-Approved-USB` and add allowed devices by **Vendor ID / Product ID** (typically corporate-encrypted hardware such as IronKey, Kingston IronKey D300S, or Apricorn Aegis).
3. Save. All non-listed removable storage will be subject to DLP rule actions when policies reference this group.

### Service domain groups

1. Select **Service domains** → set the default to **Block** (Zone 3) or **Audit** (Zone 1/2).
2. Add allowed corporate domains (`*.contoso.com`, `*.sharepoint.com`).
3. Add an **Unmanaged AI services** block group with: `chat.openai.com`, `chatgpt.com`, `gemini.google.com`, `claude.ai`, `deepseek.com`, `perplexity.ai`, `you.com`, `pi.ai`.

### Browser and domain restrictions to sensitive data

1. Select **Browser and domain restrictions to sensitive data**.
2. Under **Unallowed browsers**, add `chrome.exe` and `firefox.exe` for **Zone 3** to require Edge for Business for sensitive content workflows.

### Always audit file activity for devices

1. Confirm **Always audit file activity for devices** is **On**. Required for forensic evidence under FINRA 4511 and SEC 17a-4(f) record-keeping.

### Just-in-time protection

1. Open **Just-in-time protection** and enable for **All file activity for devices**.
2. Configure the **Fallback action** to **Block** (Zone 3) or **Audit** (Zone 1/2) for activities that cannot reach the cloud policy service.
3. See [Microsoft Learn: Get started with just-in-time protection](https://learn.microsoft.com/en-us/purview/endpoint-dlp-get-started-jit) for full configuration.

---

## Step 3 — Create the Endpoint DLP Policy

1. In **Microsoft Purview > Data Loss Prevention > Policies**, click **+ Create policy**.
2. **Categories**: select **Custom** → **Custom policy**.
3. **Name**: use a zone-prefixed convention, e.g., `FSI-Z3-Endpoint-FinancialData`.
4. **Admin units**: leave at full directory unless your tenant uses scoped admin units.
5. **Locations**: turn on **Devices** only (this walkthrough). Enable **Microsoft Edge** in Step 5 below.
6. **Policy settings**: select **Create or customize advanced DLP rules**.
7. **Rules**: click **+ Create rule**.
   - **Name**: `Block-Sensitive-Financial-Data-Devices`
   - **Conditions** → **Content contains** → **Sensitive info types**: add `U.S. Social Security Number (SSN)`, `Credit Card Number`, `U.S. Bank Account Number`, `ABA Routing Number`, plus any custom FSI SITs from Control 1.13. Set **Min count: 1** and **Confidence: High (85)**.
   - **Actions** → **Audit or restrict activities on devices**: configure each activity per the zone matrix in [Step 4](#step-4-configure-zone-specific-actions).
   - **User notifications**: enable policy tip with text: `This content contains sensitive financial information. Per firm policy, this action is restricted. Contact compliance@<firm> for assistance.`
   - **User overrides**: enable for Zone 2 with **business justification required**; disable for Zone 3.
   - **Incident reports**: send to `dlp-alerts@<firm>` at **High** severity for block events.
8. **Policy mode**: select **Run the policy in simulation mode with policy tips** for the pilot phase.
9. **Submit**.

---

## Step 4 — Configure Zone-Specific Actions

Apply per-activity actions on the rule's **Audit or restrict activities on devices** section.

| Activity | Zone 1 (Personal) | Zone 2 (Team) | Zone 3 (Enterprise) |
|---|---|---|---|
| Upload to a restricted cloud service domain | Audit | Block with override | Block |
| Paste to supported browsers | Audit | Audit | Block |
| Copy to a USB removable media device | Audit | Block with override | Block |
| Copy to a network share | Audit | Audit | Block |
| Print | Audit | Audit | Block |
| Copy or move using unallowed Bluetooth app | Audit | Block | Block |
| Remote Desktop (RDP) | Audit | Audit | Block |
| Access by restricted apps | Audit | Block with override | Block |
| Edge for Business inline AI prompts and uploads | Audit (recommended) | Block with override (recommended) | Block (required) |

---

## Step 5 — Enable Edge for Business Inline AI DLP

1. Edit the policy from Step 3.
2. On the **Locations** page, toggle **Microsoft Edge for Business** to **On**.
3. Add the rule action **Audit or restrict activities in Microsoft Edge for Business** with sub-activities:
   - **Submit prompts to a generative AI service**: Block (Zone 3), Block with override (Zone 2), Audit (Zone 1)
   - **Upload files to a generative AI service**: Block (Zone 3), Block with override (Zone 2), Audit (Zone 1)
   - **Paste sensitive content into a generative AI service**: as above
4. Optionally enable **Redirect users to Microsoft 365 Copilot** when blocking (Zone 3) to channel users to the sanctioned tenant-protected experience.
5. Save the policy.

!!! tip "Edge for Business does not require device onboarding"
    Inline DLP in Edge for Business operates on any device where the user signs in with their Entra work account, including unmanaged BYOD. This provides coverage before Defender for Endpoint deployment is complete.

---

## Step 6 — Configure Network DLP via Global Secure Access (Zone 2 Recommended, Zone 3 Required)

1. Sign in to **Microsoft Entra admin center** (`https://entra.microsoft.com`).
2. Navigate to **Global Secure Access** → **Secure** → **Security profiles**.
3. Click **+ Create profile**, name it `FSI-AI-DLP-Profile`, set priority appropriately (lower number = higher priority).
4. Add **Web content filtering policies** that route traffic to unmanaged AI services through the inspection engine.
5. Link the DLP policy created in Step 3 under **Linked policies**.
6. Assign the security profile to user groups via **Conditional Access** policy under **Identity > Protection > Conditional Access**.
7. Validate with the Global Secure Access client installed on a test device.

!!! warning "Licensing dependency"
    Global Secure Access network DLP requires **Microsoft Entra Suite** or the **Global Secure Access standalone** SKU. Verify entitlement before enabling for production.

---

## Step 7 — Enable DLP for Windows Recall (Copilot+ PCs)

1. In **Purview > Endpoint DLP settings**, locate **DLP for Windows Recall** (rolling out in 2026; check release ring).
2. Enable the toggle and confirm the policy applies to your Copilot+ PC device group.
3. Configure the action: **Exclude sensitive content from Recall snapshots** (recommended for all zones where Recall is permitted by Control 1.20).

---

## Step 8 — Pilot, Validate, then Enforce

1. Run the policy in **simulation mode with policy tips** for **7–14 days** with the pilot device group.
2. Review **Purview > Data Loss Prevention > Activity explorer** daily for false positives and tune SIT confidence levels (per Control 1.13).
3. Document false-positive analysis and tuning decisions in your CAB ticket — required evidence for FINRA 3110 supervisory review.
4. After pilot validation, edit the policy and switch **Policy mode** to **Turn the policy on**.
5. Communicate the change in advance to all affected users with the policy tip wording and override workflow.

---

## Configuration by Governance Level (Summary)

| Setting | Baseline (Zone 1) | Recommended (Zone 2) | Regulated (Zone 3) |
|---|---|---|---|
| Device onboarding | Required | Required | Required |
| USB transfer | Audit | Block with override | Block |
| Cloud upload (unmanaged) | Audit | Block with override | Block |
| Print | Audit | Audit | Block |
| Clipboard to restricted apps | Audit | Audit | Block |
| Bluetooth | Allowed | Block | Block |
| Network share (unauthorized) | Audit | Audit | Block |
| Edge for Business inline AI DLP | Audit (recommended) | Block with override (recommended) | Block (required) |
| Global Secure Access network DLP | Not required | Recommended | Required |
| DLP for Windows Recall | Audit if applicable | Exclude sensitive content | Exclude sensitive content |
| Just-in-time protection | Enabled | Enabled | Enabled |
| User overrides | N/A (audit) | Allowed with business justification | Disabled |

---

## Validation Checklist

- [ ] All target devices show **Onboarded** in Purview and **Active / Healthy** in Defender
- [ ] Endpoint DLP policy is **On** (or in simulation during pilot) and scoped to correct device groups
- [ ] Restricted apps, removable storage, and service domain groups reflect the FSI catalog
- [ ] Edge for Business inline AI DLP is enabled per zone
- [ ] Global Secure Access security profile linked (Zone 2/3)
- [ ] Just-in-time protection is **On** with appropriate fallback action
- [ ] Pilot results documented; CAB approval recorded for enforcement transition

---

[Back to Control 1.17](../../../controls/pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
