# Verification & Testing: Control 1.17 - Endpoint Data Loss Prevention

**Last Updated:** February 2026

## Manual Verification Steps

### Test 1: Verify Device Onboarding

1. Open Microsoft Defender portal
2. Navigate to Assets > Devices
3. Verify target devices show "Active" status
4. **EXPECTED:** All target devices onboarded and healthy

### Test 2: Test USB Transfer Block

1. Create test document with sensitive data (SSN pattern)
2. Attempt to copy to USB drive
3. **EXPECTED:** Block message appears (Zone 2/3) or audit logged (Zone 1)

### Test 3: Test Cloud Upload Block

1. Create test document with credit card pattern
2. Attempt to upload to personal Dropbox/Google Drive
3. **EXPECTED:** Upload blocked with policy tip

### Test 4: Test Clipboard Restriction

1. Copy sensitive content from labeled document
2. Attempt to paste into restricted application (e.g., Telegram)
3. **EXPECTED:** Paste blocked or audited per policy

### Test 5: Verify Activity Logging

1. Perform one of the above test actions
2. Open Microsoft Purview > Activity Explorer
3. Search for the test event
4. **EXPECTED:** Event logged with device details

### Test 6: Browser-Based DLP in Edge for Business

1. Open Microsoft Edge for Business
2. Navigate to an AI web app (e.g., ChatGPT, Gemini)
3. Paste test content containing a sensitive information pattern (e.g., SSN)
4. **EXPECTED:** DLP policy tip appears; action is blocked, warned, or audited per policy configuration

### Test 7: Network Data Security (Global Secure Access)

1. With Global Secure Access client installed, attempt to access an unmanaged AI application
2. Submit test content containing sensitive data via the network-protected path
3. **EXPECTED:** DLP policy intercepts the request; sensitive data transfer is blocked or audited per security profile

---

## Test Cases

| Test ID | Scenario | Expected Result | Pass/Fail |
|---------|----------|-----------------|-----------|
| TC-1.17-01 | Device onboarding status | Active and healthy | |
| TC-1.17-02 | USB transfer of labeled doc | Blocked/Audited per zone | |
| TC-1.17-03 | Upload to unauthorized cloud | Blocked with tip | |
| TC-1.17-04 | Clipboard to restricted app | Blocked/Audited | |
| TC-1.17-05 | Print sensitive document | Audited/Blocked per zone | |
| TC-1.17-06 | Activity logged | Event in explorer | |
| TC-1.17-07 | Offline enforcement | Policy enforced offline | |
| TC-1.17-08 | Browser DLP in Edge | Policy tip on AI web app paste | |
| TC-1.17-09 | Network DLP via GSA | Sensitive data blocked at network | |

---

## Evidence Collection Checklist

### Device Onboarding

- [ ] Screenshot: Defender portal device list
- [ ] Export: Device inventory with DLP status

### Policy Configuration

- [ ] Screenshot: Endpoint DLP settings
- [ ] Screenshot: Restricted apps list
- [ ] Export: DLP policy configuration

### Test Results

- [ ] Screenshot: USB block notification
- [ ] Screenshot: Cloud upload block
- [ ] Screenshot: Activity Explorer events
- [ ] Screenshot: Edge for Business DLP policy tip on AI web app
- [ ] Screenshot: Global Secure Access network DLP block event

### Compliance Evidence

- [ ] Export: Activity log for test period
- [ ] Document: Test results summary

---

## Evidence Artifact Naming Convention

```
Control-1.17_[ArtifactType]_[YYYYMMDD].[ext]

Examples:
- Control-1.17_DeviceInventory_20260115.csv
- Control-1.17_DLPPolicyConfig_20260115.png
- Control-1.17_USBBlockTest_20260115.png
- Control-1.17_ActivityExport_20260115.csv
```

---

## Attestation Statement Template

```markdown
## Control 1.17 Attestation - Endpoint DLP

**Organization:** [Organization Name]
**Control Owner:** [Name/Role]
**Date:** [Date]

I attest that:

1. Target devices are onboarded to Microsoft Defender for Endpoint
   - Total devices: [Count]
   - Healthy status: [Count]

2. Endpoint DLP is enabled with appropriate policies:
   - Zone 1 policies: [Count]
   - Zone 2 policies: [Count]
   - Zone 3 policies: [Count]

3. Restricted applications are configured:
   - [List key restricted apps]

4. USB/Removable media restrictions are configured:
   - Zone 1: [Audit]
   - Zone 2: [Block with override]
   - Zone 3: [Block]

5. Activities are logged and available for compliance review

6. Browser-based DLP is enabled for Edge for Business:
   - DLP location configured: [Yes/No]
   - AI web app monitoring active: [Yes/No]

7. Network Data Security via Global Secure Access:
   - Security profiles configured: [Yes/No]
   - AI service endpoints monitored: [Yes/No]

**Policy Mode:** [Test/Enforce]
**Last Policy Update:** [Date]

**Signature:** _______________________
**Date:** _______________________
```

---

[Back to Control 1.17](../../../controls/pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
