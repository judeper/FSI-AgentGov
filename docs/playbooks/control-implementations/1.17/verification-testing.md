# Verification & Testing: Control 1.17 — Endpoint Data Loss Prevention

**Last Updated:** April 2026
**Audience:** M365 administrators, compliance officers, internal/external auditors

This playbook provides numbered, repeatable test procedures with documented expected results and the auditor evidence to capture for each scenario. Tests are zone-aware; perform the row appropriate to the device's governance zone.

---

## Pre-Test Setup

Before running any test:

1. Confirm pilot device(s) are onboarded — see [Portal Walkthrough](portal-walkthrough.md), Step 1.
2. Confirm the Endpoint DLP policy is in **Test with notifications** or **Enable** mode (not **Disable**).
3. Have the test data set ready:
   - **Synthetic SSN test file** (`SSN-test.txt`) containing the safe Microsoft test pattern `123-45-6789` repeated 3 times (avoid using real production data — required by SEC Reg S-P).
   - **Synthetic credit card test file** (`CC-test.txt`) containing `4532-7153-3790-1264` (a valid Luhn but unallocated PAN block).
   - **Synthetic ABA routing file** (`ABA-test.txt`) containing `021000021` (J.P. Morgan Chase test routing).
4. Document tester identity, device name, zone, date, and policy mode in the test log.

!!! warning "Use synthetic test data only"
    Never use production customer NPI for DLP testing. SEC Regulation S-P (17 CFR 248.30) and GLBA Safeguards Rule require minimization of NPI handling, including in test scenarios.

---

## Verification Checklist (Numbered)

### 1. Device Onboarding Health

| Step | Action | Expected Result |
|---|---|---|
| 1.1 | Open `https://purview.microsoft.com` → **Settings** → **Device onboarding** → **Devices**. | Test device appears with **Onboarded** status and **Last seen** within last 24 hours. |
| 1.2 | Open `https://security.microsoft.com` → **Assets** → **Devices** → select test device. | **Health state: Active**, **Sensor health: Healthy**, **OS platform** matches expected. |
| 1.3 | On the device, run `Get-MpComputerStatus` (Windows) and confirm `AMServiceEnabled = True` and `RealTimeProtectionEnabled = True`. | Both values are `True`. |

**Auditor evidence:**

- Screenshot: Purview Devices list with test device row highlighted
- Screenshot: Defender device detail page (health, sensor, OS)
- CSV export of full device inventory (Defender > Assets > Devices > Export)

---

### 2. USB / Removable Media Block

| Step | Action | Expected Result (Zone 1) | Expected Result (Zone 2) | Expected Result (Zone 3) |
|---|---|---|---|---|
| 2.1 | Insert a non-allowlisted USB drive into the test device. | Drive mounts. | Drive mounts. | Drive mounts but file writes are blocked. |
| 2.2 | Copy `SSN-test.txt` to the USB drive. | Copy succeeds; **audit event logged**. | **Block dialog** with override option; entering business justification permits copy. | **Block dialog**; copy is **denied with no override**. |
| 2.3 | Insert an allowlisted (corporate-encrypted) USB and repeat. | Copy succeeds; logged. | Copy succeeds; logged. | Copy succeeds; logged. |

**Auditor evidence:**

- Screenshot: User-facing block notification with policy tip text visible
- Screenshot: Override dialog (Zone 2) with business justification field
- Activity Explorer event export filtered to test user + last 1 hour

---

### 3. Cloud Upload Block (Personal Cloud Storage)

| Step | Action | Expected Result |
|---|---|---|
| 3.1 | Open a browser and sign in to a personal Dropbox / Google Drive / iCloud account. | Sign-in succeeds (sign-in is not blocked). |
| 3.2 | Attempt to upload `CC-test.txt`. | Zone 1: audit; Zone 2: block with override; Zone 3: block. Policy tip displayed. |
| 3.3 | Repeat with the OneDrive consumer client (`OneDrive.exe` consumer profile). | Same result; restricted-apps enforcement triggers. |

**Auditor evidence:**

- Screenshot: Block notification on the cloud service web page
- Activity Explorer entry showing cloud service domain match

---

### 4. Restricted Application Block

| Step | Action | Expected Result |
|---|---|---|
| 4.1 | Launch a restricted app (e.g., Telegram, Discord, WhatsApp Desktop). | App launches. |
| 4.2 | Open `SSN-test.txt`, copy contents to clipboard, and paste into the app. | Zone 1: audit; Zone 2: block with override; Zone 3: block. Policy tip displayed. |
| 4.3 | Try to attach `SSN-test.txt` directly via the app's file picker. | File access blocked or audited per zone. |

**Auditor evidence:**

- Screenshot: Paste blocked with policy tip
- Activity Explorer entry showing target app name

---

### 5. Edge for Business Inline AI DLP

| Step | Action | Expected Result |
|---|---|---|
| 5.1 | Open Microsoft Edge for Business, signed in with the Entra work account. | Browser shows the work-profile briefcase indicator. |
| 5.2 | Navigate to `https://chatgpt.com` (or `https://gemini.google.com`). | Page loads. |
| 5.3 | Paste contents of `SSN-test.txt` into the prompt box and press send. | Zone 1: audit; Zone 2: block with override; Zone 3: block + (if configured) redirect link to Microsoft 365 Copilot. |
| 5.4 | Attempt to upload `CC-test.txt` via the AI service's file upload control. | Same per-zone result. |
| 5.5 | Repeat steps 5.2–5.4 in **Chrome** or **Firefox** (Zone 3 only). | Browser is on the **Unallowed browsers** list — sensitive content access is blocked at the file level when SIT match is detected. |

**Auditor evidence:**

- Screenshot: Edge inline DLP policy tip on AI prompt submission
- Screenshot: Redirect-to-Copilot dialog (if configured)
- Activity Explorer entry with `Application: Microsoft Edge` and AI service URL

---

### 6. Network DLP via Global Secure Access (Zone 2 / Zone 3)

| Step | Action | Expected Result |
|---|---|---|
| 6.1 | Confirm Global Secure Access client is installed and connected on the test device. | Client shows **Connected** status in the system tray. |
| 6.2 | Use a non-Edge browser or a CLI tool (e.g., `curl https://chat.openai.com/...`) to submit sensitive content through the GSA tunnel. | GSA security profile intercepts and applies DLP action per zone. |
| 6.3 | Disable Edge for Business inline DLP temporarily on a test policy (or use an unmanaged browser) and confirm GSA still enforces. | Network-level enforcement holds without browser-level dependency. |

**Auditor evidence:**

- Screenshot: GSA client connection status
- Defender XDR > Investigation & response > Activity log entry showing GSA-sourced DLP event

---

### 7. Just-in-Time Protection (Offline Enforcement)

| Step | Action | Expected Result |
|---|---|---|
| 7.1 | Disconnect the test device from all networks (disable Wi-Fi and unplug Ethernet). | Device is offline. |
| 7.2 | Wait 5 minutes (allows JIT cache to engage). | — |
| 7.3 | Attempt USB copy of `SSN-test.txt`. | Action is blocked / audited per the **Just-in-time protection** fallback action. |
| 7.4 | Reconnect the network. | Cached audit events sync to Activity Explorer within 30 minutes. |

**Auditor evidence:**

- Screenshot: Offline block notification
- Activity Explorer event with timestamp matching the offline test window

---

### 8. DLP for Windows Recall (Copilot+ PCs only)

| Step | Action | Expected Result |
|---|---|---|
| 8.1 | On a Copilot+ PC with Recall enabled, open `SSN-test.txt` and leave it visible for 60 seconds. | Recall snapshot is captured. |
| 8.2 | Open Recall and search for `123-45-6789`. | Search returns no result; the snapshot containing sensitive content is excluded by DLP. |

**Auditor evidence:**

- Screenshot: Recall search returning no results for the SIT pattern
- Purview Activity Explorer entry showing Recall exclusion event

---

### 9. Activity Explorer Logging Completeness

| Step | Action | Expected Result |
|---|---|---|
| 9.1 | Open `https://purview.microsoft.com` → **Solutions** → **Data Loss Prevention** → **Activity explorer**. | Page loads. |
| 9.2 | Filter on **Date: last 24h**, **Activity: DLP rule matched**, **User: <test user>**. | All test events from sections 2–8 are present. |
| 9.3 | Click into a single event and verify required fields are populated: device name, user UPN, file path, SIT match with confidence, rule name, action taken. | All fields populated. |
| 9.4 | Export filtered results to CSV. | Export downloads with all event details. |

**Auditor evidence:**

- CSV export of Activity Explorer (filtered to test window)
- Screenshot: Single-event detail page with all fields visible

---

### 10. Role and Access Verification

| Step | Action | Expected Result |
|---|---|---|
| 10.1 | In **Purview > Roles & scopes > Permissions**, list members of **Compliance Administrator**. | Only authorized **Purview Compliance Admin** identities; no Power Platform Admin or general user. |
| 10.2 | Confirm device-onboarding cmdlet/portal access is restricted to **Entra Security Admin**. | Verified via Entra ID role assignment review. |
| 10.3 | Verify break-glass / standing-elevation accounts are PIM-eligible, not active. | PIM shows **Eligible** assignments only for non-emergency principals. |

**Auditor evidence:**

- Export: Role group membership CSV
- Export: PIM eligible vs. active assignment report

---

## Test Case Tracking Matrix

| Test ID | Zone | Scenario | Expected | Result | Evidence Artefact | Tester | Date |
|---|---|---|---|---|---|---|---|
| TC-1.17-01 | All | Device onboarded and healthy | Active/Healthy | | DeviceInventory.csv | | |
| TC-1.17-02 | 1 | USB copy — audit-only | Logged, not blocked | | USB-Z1-Audit.png | | |
| TC-1.17-03 | 2 | USB copy — block with override | Block + override option | | USB-Z2-Override.png | | |
| TC-1.17-04 | 3 | USB copy — hard block | Block, no override | | USB-Z3-Block.png | | |
| TC-1.17-05 | 2/3 | Cloud upload to Dropbox | Block per zone | | CloudUpload.png | | |
| TC-1.17-06 | 2/3 | Restricted app paste (Telegram) | Block per zone | | RestrictedApp.png | | |
| TC-1.17-07 | 1/2/3 | Edge inline DLP on ChatGPT | Action per zone | | EdgeAI.png | | |
| TC-1.17-08 | 3 | Edge AI block + Copilot redirect | Redirect dialog | | CopilotRedirect.png | | |
| TC-1.17-09 | 2/3 | GSA network DLP | Network-level block | | GSA-Block.png | | |
| TC-1.17-10 | All | JIT offline enforcement | Block while offline | | JIT-Offline.png | | |
| TC-1.17-11 | All (Copilot+) | Recall exclusion | No SIT in Recall search | | Recall-NoResult.png | | |
| TC-1.17-12 | All | Activity Explorer completeness | All events with full fields | | ActivityExport.csv | | |
| TC-1.17-13 | All | Role least privilege | No over-privileged identities | | RoleMembership.csv | | |

---

## Evidence Bundle Layout (for Auditor Delivery)

```
Control-1.17_Evidence_<YYYYMMDD>/
├── 01-device-onboarding/
│   ├── DeviceInventory_<date>.csv
│   ├── DeviceInventory_<date>.csv.sha256
│   └── PurviewDevicesList_<date>.png
├── 02-policy-configuration/
│   ├── Control-1.17_Posture.csv
│   ├── Control-1.17_Posture.json
│   ├── EndpointDLPSettings_RestrictedApps_<date>.png
│   ├── EndpointDLPSettings_RemovableStorage_<date>.png
│   └── EndpointDLPSettings_ServiceDomains_<date>.png
├── 03-test-results/
│   ├── TC-1.17-02_USB-Z1-Audit_<date>.png
│   ├── TC-1.17-04_USB-Z3-Block_<date>.png
│   ├── TC-1.17-07_EdgeAI_<date>.png
│   └── ... (one per test case)
├── 04-activity-explorer/
│   └── ActivityExport_<window>.csv
├── 05-roles/
│   └── RoleMembership_<date>.csv
└── Attestation_Control-1.17_<date>.md
```

Generate SHA-256 hashes for every artefact (see [PowerShell Setup](powershell-setup.md) for the canonical pattern). Supports SEC Rule 17a-4(f)(2)(ii) WORM-equivalent integrity requirements.

---

## Attestation Statement Template

```markdown
## Control 1.17 Attestation — Endpoint Data Loss Prevention

**Organization:** [Legal entity name and CRD/IARD number]
**Control Owner:** [Name, role, e-mail]
**Test Window:** [Start date] — [End date]
**Policy Mode at Test:** [TestWithNotifications | Enable]
**Tester(s):** [Name, role]

I attest that on the date above, the following controls were validated against the FSI Agent Governance Framework v1.3.3 Control 1.17:

1. **Device Onboarding** — [Total devices] target devices were onboarded to Microsoft Defender for Endpoint with healthy status; [Total] showed last activity within 24 hours.
2. **Policy Coverage** — Endpoint DLP policies in scope: Zone 1 [count], Zone 2 [count], Zone 3 [count]. All policies in mode [Test/Enable].
3. **Restricted Applications** — Configured app groups: [list]. Tested actions returned expected results per zone.
4. **Removable Media** — USB allowlist contains [N] approved devices. Test of non-allowlisted USB returned [Audit/Block/Block-with-override] per zone.
5. **Cloud Upload Restrictions** — Service domain block list includes [unmanaged AI services count] AI services and [N] consumer cloud services.
6. **Edge for Business Inline AI DLP** — Enabled for [zones]. Test paste / upload to ChatGPT and Gemini returned expected per-zone result.
7. **Global Secure Access Network DLP** — [Enabled/Not applicable]. Security profile [name] linked to DLP policy [name].
8. **Just-in-Time Protection** — Enabled with fallback action [Block/Audit]; offline test confirmed enforcement.
9. **Activity Explorer** — All [N] test events present with full device, user, file, SIT, and rule details.
10. **Role Assignments** — Compliance Administrator and Security Administrator group membership reviewed; no over-privileged identities observed.

Evidence bundle SHA-256 manifest is attached.

**Signature:** ______________________________
**Date:** ______________________________
```

---

[Back to Control 1.17](../../../controls/pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
