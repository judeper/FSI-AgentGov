# Troubleshooting: Control 1.17 — Endpoint Data Loss Prevention

**Last Updated:** May 2026

This playbook lists the most common issues encountered when deploying and operating Endpoint DLP. Each issue follows a consistent format: **Symptoms → Likely Cause → Diagnostic Steps → Fix → Reference**.

---

## Quick Reference Table

| Issue | Likely Cause | Quick Fix |
|---|---|---|
| Device not visible in Purview | Onboarding incomplete or duplicate Defender enrollment | Re-deploy onboarding package via Intune; verify only one MDE tenant |
| Policy created but nothing enforced | Policy in **Disable** or **TestWithoutNotifications** mode | Set `-Mode Enable` after pilot |
| USB blocks not firing | Device not in policy scope or USB on allowlist | Adjust scope; check Vendor/Product ID allowlist |
| Edge inline AI DLP not triggering | Edge for Business location not toggled on policy, or user not signed in to work profile | Enable **Microsoft Edge for Business** on policy; verify work-profile briefcase |
| Activity Explorer empty | Audit logging off or device not synced | Enable **Always audit file activity for devices**; wait 30 minutes |
| High false-positive rate | SIT confidence threshold too low | Raise to **High (85)**; add exclusions; tune SITs in Control 1.13 |
| GSA network DLP not blocking | Security profile not linked to DLP policy or licensing missing | Link DLP policy in security profile; verify Entra Suite SKU |
| macOS device fewer enforcement options | macOS feature gap | Use Edge for Business + GSA for macOS coverage |
| User cannot override (Zone 2) | Override disabled on rule, or no business justification provided | Enable `AllowOverride` on rule; require justification text |
| Recall still indexes sensitive content | DLP for Recall not enabled or device not Copilot+ | Enable in Endpoint DLP settings; confirm Copilot+ hardware |

---

## Issue: Device Not Appearing in Purview Devices List

### Symptoms

- Device is enrolled in Intune and onboarded to Defender for Endpoint, but does not appear in **Purview > Settings > Device onboarding > Devices**.
- DLP policies do not enforce on the device even though policy scope includes it.

### Likely Cause

- Onboarding telemetry has not yet synced (first sync can take up to 24 hours).
- Defender for Endpoint is enrolled in a **different tenant** (legacy migration or duplicate enrollment).
- License is missing or scoped to the wrong user (Endpoint DLP requires E5 / E5 Compliance / E5 Security).

### Diagnostic Steps

1. On the device run `Get-MpComputerStatus | Select-Object AMServiceEnabled, AntivirusEnabled, RealTimeProtectionEnabled, AntispywareEnabled` (Windows). All should be `True`.
2. Check the local sensor health log at `C:\ProgramData\Microsoft\Windows Defender Advanced Threat Protection\SenseCM\` for onboarding errors.
3. In the Defender portal, **Assets > Devices**, confirm device is **Active** and look for the **Domain joined / Azure AD joined** indicator.
4. Run the [Defender for Endpoint Client Analyzer](https://learn.microsoft.com/en-us/defender-endpoint/overview-client-analyzer) and review the report.
5. Confirm the user signed in to the device has a license that includes Endpoint DLP via **Entra > Users > <user> > Licenses**.

### Fix

- Wait 24 hours for first telemetry sync if onboarding is fresh.
- Re-deploy the Intune endpoint detection and response policy and force a sync (`Settings > Accounts > Access work or school > Sync`).
- If a duplicate Defender enrollment exists, run the offboarding script from the previous tenant before re-onboarding.
- Assign the correct E5/E5-Compliance license and wait for the next policy refresh cycle.

---

## Issue: Policy Created but Nothing Is Enforced

### Symptoms

- Test transfers (USB, cloud upload, paste) that should be blocked are succeeding.
- No policy tip appears.
- Activity Explorer shows no DLP events for the test user.

### Likely Cause

- Policy is in **TestWithoutNotifications** mode (silent simulation).
- Policy **Devices** location is disabled, even though the policy was created with Endpoint DLP.
- Rule conditions do not match (SIT confidence too high, minCount > content match, label scope mismatch).
- Device is not in the policy's scope (admin unit, group, or user filter excludes it).

### Diagnostic Steps

1. Run `Get-DlpCompliancePolicy -Identity <PolicyName> | Select-Object Name, Mode, EndpointDlpLocation, Enabled` and confirm `Mode = Enable` and `EndpointDlpLocation` includes `All` or the relevant scope.
2. Run `Get-DlpComplianceRule -Policy <PolicyName>` and inspect each rule's `BlockAccess`, `ContentContainsSensitiveInformation`, and `Disabled` properties.
3. In the portal, open the policy → **Locations** → confirm **Devices** toggle is on and the included groups contain your test user/device.
4. Confirm the test file actually contains a SIT match: open **Purview > Data classification > Content explorer** and search for the test file path.

### Fix

- Switch policy to **Enable** mode after pilot validation.
- Toggle **Devices** location on and re-add device groups to scope.
- Lower SIT `confidencelevel` to `Medium` for diagnostic testing, then return to `High` for production.
- If multiple policies cover the same content, set rule **Priority** so the blocking rule wins.

---

## Issue: USB / Removable Media Not Blocked

### Symptoms

- A non-corporate USB drive is plugged in and accepts file copies of content matching SITs.
- No block dialog or audit event.

### Likely Cause

- USB device is on the **Removable storage device groups** allowlist (matched by Vendor ID or Product ID).
- The DLP rule's **Copy to a USB removable media device** action is set to **Audit**, not **Block**.
- USB enforcement requires Defender for Endpoint device control to be enabled in tandem.

### Diagnostic Steps

1. Plug in the USB and run `Get-PnpDevice -Class USB` to capture the **Vendor ID (VID)** and **Product ID (PID)**.
2. Compare against **Purview > Endpoint DLP settings > Removable storage device groups** allowlist entries.
3. Inspect the rule action: in the portal, **Policies > <policy> > Edit > Rule > Actions > Audit or restrict activities on devices > Copy to a USB removable media device**.
4. Confirm Defender for Endpoint device control is enabled at `Microsoft Intune > Endpoint security > Attack surface reduction > Device control`.

### Fix

- Remove the device from the allowlist or narrow the allowlist to specific instance IDs.
- Set the action to **Block** (Zone 3) or **Block with override** (Zone 2).
- Enable Defender for Endpoint device control profile via Intune.

---

## Issue: Edge for Business Inline AI DLP Not Triggering

### Symptoms

- Pasting sensitive content into ChatGPT, Gemini, or another GenAI service inside Edge for Business does not produce a policy tip or block.
- Edge inline DLP works for some users but not others.

### Likely Cause

- The DLP policy does not have **Microsoft Edge for Business** enabled in the **Locations** step.
- The user is not signed in to the **work profile** in Edge — inline DLP requires the briefcase indicator.
- The Edge channel is older than the minimum supported version (verify on [Microsoft Learn](https://learn.microsoft.com/en-us/purview/dlp-browser-dlp-learn)).
- The destination domain is not yet in Microsoft's curated GenAI list and no custom service domain rule is configured.

### Diagnostic Steps

1. In the policy, confirm **Locations > Microsoft Edge for Business** is **On**.
2. In Edge, click the profile icon — confirm the **Work** profile (briefcase icon) is selected.
3. Check Edge version: `edge://version`. Compare against the supported minimum.
4. Open `edge://policy/` and confirm the `EnterpriseModeSiteList` and DLP-related policies are pushed.
5. For unrecognized AI services, add the domain to **Endpoint DLP settings > Service domains** and reference it in the rule action.

### Fix

- Toggle the Edge for Business location on and re-publish the policy.
- Switch the user to the work profile, or enforce profile selection via Intune browser policy.
- Update Edge to current channel via Intune update rings.
- Add custom AI service domains to the service domain group and re-publish.

---

## Issue: Activity Explorer Shows No Events

### Symptoms

- Test actions confirmed via on-device notifications, but Activity Explorer has no entries.
- DLP alerts are not generated.

### Likely Cause

- **Always audit file activity for devices** is disabled.
- Device cannot reach the Microsoft 365 audit ingestion endpoint (firewall, proxy, or sovereign-cloud endpoint mismatch).
- Audit log search has not finished indexing (events typically appear in 15–30 minutes; rarely longer).
- Test user lacks the **Audit Reader** or **View-Only DLP Compliance Management** role to see the events.

### Diagnostic Steps

1. In **Purview > Endpoint DLP settings > Always audit file activity for devices**, confirm the toggle is **On**.
2. On the device, validate egress to required Microsoft 365 endpoints per the [Microsoft 365 URLs and IP ranges list](https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges).
3. In **Purview > Audit > Search**, search for the test user and date range; if events appear here but not in Activity Explorer, the issue is RBAC.
4. Check role assignments at **Purview > Roles & scopes > Permissions**.

### Fix

- Enable the audit toggle.
- Open required firewall / proxy egress for Defender for Endpoint and Purview.
- Wait the full 30-minute ingestion window before declaring failure.
- Grant the investigating user **Compliance Administrator** or **View-Only Compliance Management** role.

---

## Issue: High False-Positive Rate

### Symptoms

- Legitimate business actions (e.g., posting account numbers in approved internal applications) are blocked.
- User complaints spike after enforcement is enabled.
- Excessive alerts overwhelm the SOC.

### Likely Cause

- SIT confidence threshold is too low (defaults to 65 / Medium) — over-matches.
- Rule lacks scoping by user group or sensitivity label.
- Custom SITs from Control 1.13 use overly broad regex patterns.

### Diagnostic Steps

1. In **Purview > Activity explorer**, filter on **Activity: DLP rule matched** and **Rule: <rule name>** for the past 7 days.
2. Group by **File extension**, **Application**, and **User** to identify false-positive clusters.
3. Open a sample event and review the **Sensitive content matched** detail — note the SIT name and confidence.

### Fix

- Raise the SIT `confidencelevel` from `Medium` to `High` (85) on the rule.
- Add **Exceptions** (e.g., `ExceptIfFromMemberOf` for an approved user group, or `ExceptIfRecipientDomainIs` for trusted partners).
- Coordinate with Control 1.13 owner to tune the underlying custom SIT patterns.
- Add specific file paths to **File path exclusions** in Endpoint DLP settings (use sparingly — document rationale).

---

## Issue: Global Secure Access Network DLP Not Blocking

### Symptoms

- Edge inline DLP catches AI prompt submissions, but the same content sent through `curl` or a non-Edge browser is not intercepted.
- GSA client shows **Connected**, but no DLP events from network path appear.

### Likely Cause

- DLP policy is not linked under the GSA security profile.
- Security profile is not assigned via Conditional Access to the test user.
- GSA traffic forwarding profile does not include the AI service URLs.
- Tenant lacks **Microsoft Entra Suite** or **Global Secure Access standalone** licensing.

### Diagnostic Steps

1. In **Entra > Global Secure Access > Secure > Security profiles**, open the profile and confirm **Linked policies** lists the Endpoint DLP policy by name.
2. In **Entra > Conditional Access**, confirm a policy assigns the security profile to the test user/group.
3. On the device, run `Get-GlobalSecureAccessClientStatus` (when available) or check the GSA client diagnostic logs.
4. Confirm SKU eligibility under **Entra > Billing > Licenses**.

### Fix

- Link the DLP policy to the security profile.
- Apply the security profile via a Conditional Access policy targeting the test user/group.
- Update the traffic forwarding profile to include the AI service URLs.
- Acquire Entra Suite or GSA standalone licensing.

---

## Issue: macOS Devices Have Fewer Enforcement Options

### Symptoms

- Configuring USB block on macOS is unavailable or limited.
- Some Endpoint DLP rule actions are greyed out for macOS scope.

### Likely Cause

- Microsoft Endpoint DLP for macOS supports a **subset** of the Windows action surface. This is a documented platform limitation, not a misconfiguration.

### Fix

- Use **Edge for Business inline AI DLP** as the primary AI prompt enforcement layer on macOS — it has full feature parity with Windows.
- Use **Global Secure Access network DLP** to cover macOS network paths.
- For removable media, use **Intune Endpoint security > Attack surface reduction > Device control** with macOS-specific configuration profiles.
- Document macOS coverage gaps in your supervisory procedures (FINRA Rule 3110(b)).

Reference: [Microsoft Learn: Onboard macOS devices](https://learn.microsoft.com/en-us/purview/device-onboarding-macos-overview).

---

## Issue: User Override Not Available in Zone 2

### Symptoms

- A Zone 2 user is blocked from a legitimate file copy and cannot click an "Override" option.
- The block dialog has no business-justification field.

### Likely Cause

- Rule has `AllowOverride = $false` (Zone 3 setting applied incorrectly to Zone 2).
- Override workflow is enabled but business-justification text was not configured.
- User notification language is missing the override CTA.

### Diagnostic Steps

1. Run `Get-DlpComplianceRule -Identity <RuleName> | Select Name, BlockAccess, AllowOverride, NotifyAllowOverride`.
2. Confirm `AllowOverride = True` and `NotifyAllowOverride` includes `WithJustification`.

### Fix

```powershell
Set-DlpComplianceRule -Identity <RuleName> `
    -AllowOverride $true `
    -NotifyAllowOverride 'WithJustification'
```

Re-test from the affected user account.

---

## Issue: Recall Still Indexes Sensitive Content

### Symptoms

- On a Copilot+ PC, opening a document with SIT matches results in Recall snapshots that surface the sensitive content in search.

### Likely Cause

- DLP for Windows Recall is not enabled on the policy.
- Device is not actually a **Copilot+ PC** (DLP for Recall requires the Copilot+ NPU baseline).
- Policy update has not yet propagated.

### Diagnostic Steps

1. In **Purview > Endpoint DLP settings**, confirm **DLP for Windows Recall** is enabled.
2. On the device, open **Settings > Privacy & security > Recall & snapshots** and confirm Recall is active.
3. Run `Get-WindowsCapability -Online | Where-Object Name -like '*Recall*'` to confirm Recall is installed.

### Fix

- Enable the DLP for Windows Recall toggle and wait for policy sync (up to 24 hours).
- For non-Copilot+ devices, treat Recall coverage as not applicable.

---

## Escalation Path

| Layer | Owner | When to Escalate |
|---|---|---|
| Policy and rule logic | **Purview Compliance Admin** | Rule does not match expected content; user override behaviour is wrong |
| Device onboarding and Defender health | **Entra Security Admin** | Device not appearing as Active; sensor unhealthy; duplicate enrollment |
| Intune deployment of onboarding package and device control | **Intune Administrator** | Onboarding package not delivered; device control profile fails to apply |
| Network DLP via GSA and Conditional Access | **Entra Security Admin** | Security profile not linked or not enforced |
| Licensing entitlement | **Entra Global Admin** | Endpoint DLP or Entra Suite licensing gap |
| Microsoft platform issues | **Microsoft Support** | Service-side outage confirmed via [Service Health](https://admin.microsoft.com/Adminportal/Home#/servicehealth) |

---

## Known Limitations (May 2026)

| Limitation | Impact | Mitigation |
|---|---|---|
| macOS feature subset | Fewer rule actions available | Compensate with Edge for Business + GSA |
| Browser scope (DLP for Cloud Apps) | Inline AI DLP on third-party browsers limited | Block Chrome/Firefox in Zone 3 via **Unallowed browsers**; require Edge for Business |
| JIT cache size | Large bursts of offline activity may exceed cache | Sync devices regularly; set fallback action to **Block** in Zone 3 |
| Mobile (iOS/Android) | Endpoint DLP does not cover mobile | Use **Mobile Application Management (MAM)** policies under Control 1.6 |
| VM / VDI nuances | Some non-persistent VMs may not retain DLP sensor state | Test on the specific VDI image; consider per-session enrollment |
| GSA licensing | Network DLP requires Entra Suite or GSA standalone | Plan Zone 3 budget accordingly; or accept endpoint-only coverage with documented residual risk |

---

[Back to Control 1.17](../../../controls/pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
